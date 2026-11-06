// Roslyn "answer key" for C# call edges.
//
// Usage: RoslynCallKey <csc.rsp> <projectDir> <repoRoot> <out.jsonl>
//
// <csc.rsp> is the exact csc argument list MSBuild used for CoreCompile (dumped by
// ../dump-csc-args.targets). We rebuild the same CSharpCompilation (same sources, defines,
// references, language version), then walk every InvocationExpression / ObjectCreation
// (explicit and target-typed `new(...)`) that sits inside a method, constructor, destructor,
// operator, property/indexer/event accessor (incl. expression-bodied property) or local function.
// For each one we ask SemanticModel.GetSymbolInfo for the target and keep only targets that are
// declared in this project's own (non-obj/) source files.
using System.Collections.Immutable;
using System.Text.Json;
using System.Text.Json.Nodes;
using Microsoft.CodeAnalysis;
using Microsoft.CodeAnalysis.CSharp;
using Microsoft.CodeAnalysis.CSharp.Syntax;
using Microsoft.CodeAnalysis.Diagnostics;
using Microsoft.CodeAnalysis.Operations;

// Optional: `--members <out.jsonl>` (last two args) writes a SECOND key with the links the call key does
// not cover: constructor initializers (`: base(...)` / `: this(...)`), property / indexer accessor uses
// (get, set, both for `+=` / `++`), and user-defined operators / conversions. The main key is unchanged.
string? membersOut = null;
if (args.Length >= 6 && args[^2] == "--members") { membersOut = args[^1]; args = args[..^2]; }
if (args.Length != 4 && args.Length != 6)
{
    Console.Error.WriteLine("usage: RoslynCallKey <csc.rsp> <projectDir> <repoRoot> <out.jsonl> [--write-preprocessed <copyRoot>]");
    return 2;
}
var rspPath = args[0];
var projectDir = Path.GetFullPath(args[1]);
var repoRoot = Path.GetFullPath(args[2]);
var outPath = args[3];

var rspLines = File.ReadAllLines(rspPath).Where(l => l.Length > 0).ToArray();
var sdkDir = Path.GetDirectoryName(typeof(object).Assembly.Location);
var cmd = CSharpCommandLineParser.Default.Parse(rspLines, projectDir, sdkDir);
foreach (var d in cmd.Errors) Console.Error.WriteLine($"[cmdline] {d}");

var parseOptions = cmd.ParseOptions;
var trees = new List<SyntaxTree>();
foreach (var sf in cmd.SourceFiles)
{
    var text = File.ReadAllText(sf.Path);
    trees.Add(CSharpSyntaxTree.ParseText(text, parseOptions, sf.Path));
}
var refs = new List<MetadataReference>();
foreach (var r in cmd.MetadataReferences)
{
    var p = Path.IsPathRooted(r.Reference) ? r.Reference : Path.Combine(projectDir, r.Reference);
    refs.Add(MetadataReference.CreateFromFile(p, r.Properties));
}
var compOptions = cmd.CompilationOptions
    .WithSourceReferenceResolver(SourceFileResolver.Default)
    .WithMetadataReferenceResolver(null)
    .WithStrongNameProvider(null)
    .WithCryptoKeyFile(null)
    .WithCryptoPublicKey(ImmutableArray<byte>.Empty)
    .WithDelaySign(null)
    .WithGeneralDiagnosticOption(ReportDiagnostic.Default)
    .WithSpecificDiagnosticOptions(ImmutableDictionary<string, ReportDiagnostic>.Empty);
Compilation compilation = CSharpCompilation.Create(cmd.CompilationName ?? "Proj", trees, refs, compOptions);

// Run the source generators the real build ran, so generated members resolve (they are not "own source").
var generators = new List<ISourceGenerator>();
foreach (var a in cmd.AnalyzerReferences)
{
    try
    {
        var afr = new AnalyzerFileReference(Path.GetFullPath(a.FilePath, projectDir), AnalyzerLoader.Instance);
        generators.AddRange(afr.GetGenerators(LanguageNames.CSharp));
    }
    catch (Exception e) { Console.Error.WriteLine($"[generator-load] {a.FilePath}: {e.Message}"); }
}
if (generators.Count > 0)
{
    var driver = CSharpGeneratorDriver.Create(generators, parseOptions: parseOptions);
    driver.RunGeneratorsAndUpdateCompilation(compilation, out var updated, out var genDiags);
    compilation = updated;
}

var errors = compilation.GetDiagnostics().Where(d => d.Severity == DiagnosticSeverity.Error).ToList();
Console.Error.WriteLine($"[compile] trees={trees.Count} refs={refs.Count} generators={generators.Count} errors={errors.Count}");
foreach (var e in errors.Take(15)) Console.Error.WriteLine($"[compile-error] {e}");

string Rel(string path)
{
    var full = Path.GetFullPath(path, projectDir);
    return Path.GetRelativePath(repoRoot, full).Replace('\\', '/');
}
bool IsOwnSource(SyntaxTree? t)
{
    if (t == null || string.IsNullOrEmpty(t.FilePath)) return false;
    var full = Path.GetFullPath(t.FilePath, projectDir);
    if (!full.StartsWith(projectDir + Path.DirectorySeparatorChar)) return false;
    var rel = Path.GetRelativePath(projectDir, full).Replace('\\', '/');
    return !(rel.StartsWith("obj/") || rel.StartsWith("bin/"));
}
var ownTrees = trees.Where(IsOwnSource).ToHashSet(); // only the csc source files, never generator output

// Optional: write each own source file with #directives and inactive (#if-false) text blanked to spaces,
// preserving every line break, into <copyRoot>/<same relative path>. Used to measure how much the raw
// preprocessor text costs graphify (tree-sitter parses the file without a preprocessor).
if (args.Length == 6 && args[4] == "--write-preprocessed")
{
    var copyRoot = Path.GetFullPath(args[5]);
    int nFiles = 0, nChanged = 0;
    foreach (var t in ownTrees)
    {
        var chars = t.GetText().ToString().ToCharArray();
        bool changed = false;
        foreach (var tr in t.GetRoot().DescendantTrivia())
        {
            if (!(tr.IsDirective || tr.IsKind(SyntaxKind.DisabledTextTrivia))) continue;
            for (int i = tr.FullSpan.Start; i < tr.FullSpan.End; i++)
                if (chars[i] != '\n' && chars[i] != '\r') { chars[i] = ' '; changed = true; }
        }
        var dest = Path.Combine(copyRoot, Path.GetRelativePath(repoRoot, Path.GetFullPath(t.FilePath, projectDir)));
        Directory.CreateDirectory(Path.GetDirectoryName(dest)!);
        File.WriteAllText(dest, new string(chars));
        nFiles++; if (changed) nChanged++;
    }
    Console.Error.WriteLine($"[preprocessed] wrote {nFiles} files ({nChanged} had directives) under {copyRoot}");
}

int Line(SyntaxTree t, int pos) => t.GetLineSpan(new Microsoft.CodeAnalysis.Text.TextSpan(pos, 0)).StartLinePosition.Line + 1;

// Declaration info: decl_line = first line of the declaration node (incl. attributes),
// noattr_line = first line after attribute lists, id_line = line of the identifier.
JsonObject DeclInfo(SyntaxNode decl, string name, string kind, INamedTypeSymbol? containingType)
{
    var t = decl.SyntaxTree;
    int declLine = Line(t, decl.SpanStart);
    int noAttr = declLine;
    SyntaxToken? id = null;
    switch (decl)
    {
        case MemberDeclarationSyntax m:
            var firstNonAttr = m.ChildNodesAndTokens().FirstOrDefault(c => !(c.IsNode && c.AsNode() is AttributeListSyntax));
            if (firstNonAttr != default) noAttr = Line(t, firstNonAttr.SpanStart);
            break;
        case LocalFunctionStatementSyntax lf:
            noAttr = Line(t, (lf.Modifiers.Count > 0 ? lf.Modifiers[0] : lf.ReturnType.GetFirstToken()).SpanStart);
            break;
    }
    id = decl switch
    {
        MethodDeclarationSyntax m => m.Identifier,
        ConstructorDeclarationSyntax c => c.Identifier,
        DestructorDeclarationSyntax d => d.Identifier,
        LocalFunctionStatementSyntax l => l.Identifier,
        PropertyDeclarationSyntax p => p.Identifier,
        EventDeclarationSyntax e => e.Identifier,
        BaseTypeDeclarationSyntax b => b.Identifier,
        DelegateDeclarationSyntax dd => dd.Identifier,
        OperatorDeclarationSyntax op => op.OperatorToken,
        ConversionOperatorDeclarationSyntax co => co.ImplicitOrExplicitKeyword,
        IndexerDeclarationSyntax ix => ix.ThisKeyword,
        _ => null,
    };
    var o = new JsonObject
    {
        ["file"] = Rel(t.FilePath),
        ["line"] = declLine,
        ["noattr_line"] = noAttr,
        ["id_line"] = id.HasValue ? Line(t, id.Value.SpanStart) : declLine,
        ["type"] = containingType?.Name,
        ["type_full"] = containingType?.ToDisplayString(),
        ["name"] = name,
        ["decl_kind"] = kind,
    };
    return o;
}

JsonArray TypeDecls(INamedTypeSymbol type)
{
    var arr = new JsonArray();
    foreach (var r in type.OriginalDefinition.DeclaringSyntaxReferences)
    {
        if (!ownTrees.Contains(r.SyntaxTree)) continue;
        var node = r.GetSyntax();
        arr.Add(DeclInfo(node, type.Name, "type", type.ContainingType));
    }
    return arr;
}

// Find the "caller": innermost enclosing method-like declaration.
(SyntaxNode decl, ISymbol sym, string name, string kind)? FindCaller(SyntaxNode n, SemanticModel model, bool outer)
{
    for (var cur = n.Parent; cur != null; cur = cur.Parent)
    {
        switch (cur)
        {
            case LocalFunctionStatementSyntax lf when !outer:
                return (lf, model.GetDeclaredSymbol(lf)!, lf.Identifier.Text, "local_function");
            case MethodDeclarationSyntax m:
                return (m, model.GetDeclaredSymbol(m)!, m.Identifier.Text, "method");
            case ConstructorDeclarationSyntax c:
                return (c, model.GetDeclaredSymbol(c)!, c.Identifier.Text, "ctor");
            case DestructorDeclarationSyntax d:
                return (d, model.GetDeclaredSymbol(d)!, "~" + d.Identifier.Text, "dtor");
            case OperatorDeclarationSyntax o:
                return (o, model.GetDeclaredSymbol(o)!, "operator " + o.OperatorToken.Text, "operator");
            case ConversionOperatorDeclarationSyntax co:
                return (co, model.GetDeclaredSymbol(co)!, "operator " + co.Type, "conversion");
            case AccessorDeclarationSyntax acc:
                {
                    var owner = acc.Parent!.Parent!; // AccessorList -> Property/Indexer/Event
                    var osym = model.GetDeclaredSymbol(owner)!;
                    string oname = owner switch
                    {
                        PropertyDeclarationSyntax p => p.Identifier.Text,
                        EventDeclarationSyntax e => e.Identifier.Text,
                        IndexerDeclarationSyntax => "this[]",
                        _ => osym.Name,
                    };
                    return (owner, osym, oname, "accessor_" + acc.Keyword.Text);
                }
            case ArrowExpressionClauseSyntax arrow when arrow.Parent is PropertyDeclarationSyntax or IndexerDeclarationSyntax:
                {
                    var owner = arrow.Parent!;
                    var osym = model.GetDeclaredSymbol(owner)!;
                    string oname = owner is PropertyDeclarationSyntax p ? p.Identifier.Text : "this[]";
                    return (owner, osym, oname, "accessor_get");
                }
            case BaseTypeDeclarationSyntax:
            case FieldDeclarationSyntax:
            case EventFieldDeclarationSyntax:
            case EnumMemberDeclarationSyntax:
            case ParameterSyntax:
            case AttributeSyntax:
                return null; // field initializers, attribute args, default params: not "inside a method"
            case PropertyDeclarationSyntax:
                return null; // property initializer `= M();`
        }
    }
    return null;
}

bool InheritsFrom(INamedTypeSymbol? t, INamedTypeSymbol baseT)
{
    for (var b = t?.BaseType; b != null; b = b.BaseType)
        if (SymbolEqualityComparer.Default.Equals(b.OriginalDefinition, baseT.OriginalDefinition)) return true;
    return false;
}
bool IsOuter(INamedTypeSymbol? t, INamedTypeSymbol outerT)
{
    for (var c = t?.ContainingType; c != null; c = c.ContainingType)
        if (SymbolEqualityComparer.Default.Equals(c.OriginalDefinition, outerT.OriginalDefinition)) return true;
    return false;
}

var stats = new Dictionary<string, int>();
void Bump(string k) => stats[k] = stats.GetValueOrDefault(k) + 1;

using var w = new StreamWriter(outPath);
// Second output: every call site (incl. external / unresolved / not-in-method), used to explain graphify's extra edges.
using var ws = new StreamWriter(Path.ChangeExtension(outPath, null) + ".sites.jsonl");
string SyntacticName(SyntaxNode n) => n switch
{
    InvocationExpressionSyntax i => i.Expression switch
    {
        SimpleNameSyntax sn => sn.Identifier.Text,
        MemberAccessExpressionSyntax ma => ma.Name.Identifier.Text,
        MemberBindingExpressionSyntax mb => mb.Name.Identifier.Text,
        _ => "",
    },
    ObjectCreationExpressionSyntax oc => oc.Type switch
    {
        QualifiedNameSyntax q => q.Right.Identifier.Text,
        SimpleNameSyntax sn => sn.Identifier.Text,
        _ => oc.Type.ToString(),
    },
    _ => "new()",
};
var jsonOpts = new JsonSerializerOptions { WriteIndented = false };

// Receiver / KIND classification (works for own and external targets).
(string kind, string sub, string receiver, string receiverText, string rel) Classify(SyntaxNode node, SemanticModel model, IMethodSymbol target, INamedTypeSymbol? callerType)
{
    var def = (target.ReducedFrom ?? target).OriginalDefinition;
    var targetType = def.ContainingType;
    bool isCreation = node is BaseObjectCreationExpressionSyntax;
    bool nameIsGeneric = false;
    string receiver = "none";
    string receiverText = "";
    ExpressionSyntax? recvExpr = null;
    if (node is InvocationExpressionSyntax inv)
    {
        switch (inv.Expression)
        {
            case GenericNameSyntax: nameIsGeneric = true; receiver = "bare"; break;
            case IdentifierNameSyntax: receiver = "bare"; break;
            case MemberAccessExpressionSyntax ma:
                nameIsGeneric = ma.Name is GenericNameSyntax;
                recvExpr = ma.Expression; break;
            case MemberBindingExpressionSyntax mb:
                nameIsGeneric = mb.Name is GenericNameSyntax;
                var ca = mb.FirstAncestorOrSelf<ConditionalAccessExpressionSyntax>();
                recvExpr = ca?.Expression; receiver = "conditional"; break;
            default: receiver = "expr:" + inv.Expression.Kind(); break;
        }
        if (recvExpr != null)
        {
            receiverText = recvExpr.ToString();
            if (receiverText.Length > 60) receiverText = receiverText[..60];
            string prefix = receiver == "conditional" ? "conditional_" : "";
            if (recvExpr is ThisExpressionSyntax) receiver = prefix + "this";
            else if (recvExpr is BaseExpressionSyntax) receiver = prefix + "base";
            else
            {
                var rs = model.GetSymbolInfo(recvExpr).Symbol;
                receiver = prefix + rs switch
                {
                    INamedTypeSymbol => "type",
                    INamespaceSymbol => "namespace",
                    ILocalSymbol => "local",
                    IParameterSymbol => "parameter",
                    IFieldSymbol => "field",
                    IPropertySymbol => "property",
                    IMethodSymbol => "method_group",
                    null => "expr:" + recvExpr.Kind(),
                    _ => "other:" + rs.Kind,
                };
            }
        }
    }
    else receiver = node is ImplicitObjectCreationExpressionSyntax ? "new_implicit" : "new";

    bool isExtensionCall = target.ReducedFrom != null || target.MethodKind == MethodKind.ReducedExtension;
    bool inInterface = targetType.TypeKind == TypeKind.Interface;
    string rel =
        SymbolEqualityComparer.Default.Equals(targetType.OriginalDefinition, callerType?.OriginalDefinition) ? "same_type"
        : callerType != null && InheritsFrom(callerType, targetType) ? "base_type"
        : callerType != null && IsOuter(callerType, targetType) ? "outer_type"
        : "other_type";

    // ---- KIND (first match wins) ----
    string kind, sub = "";
    if (isCreation) kind = "ctor";
    else if (nameIsGeneric) kind = "generic";
    else if (isExtensionCall) kind = "extension";
    else if (inInterface) kind = "interface";
    else if (receiver == "type") kind = "static";
    else if (receiver is "bare" or "this" or "base" && rel == "same_type") kind = "same";
    else if (receiver is "bare" or "this" or "base" && rel == "base_type") kind = "inherited";
    else if (receiver is "local" or "parameter" or "field" or "property"
             or "conditional_local" or "conditional_parameter" or "conditional_field" or "conditional_property") kind = "typed";
    else
    {
        kind = "other";
        sub = receiver == "bare" ? (rel == "outer_type" ? "bare_outer_type" : (def.IsStatic ? "bare_using_static" : "bare_" + rel)) : "receiver_" + receiver;
    }
    return (kind, sub, receiver, receiverText, rel);
}

foreach (var tree in ownTrees.OrderBy(t => t.FilePath))
{
    var model = compilation.GetSemanticModel(tree);
    var root = tree.GetRoot();
    foreach (var node in root.DescendantNodes())
    {
        bool isInvocation = node is InvocationExpressionSyntax;
        bool isCreation = node is BaseObjectCreationExpressionSyntax;
        if (!isInvocation && !isCreation) continue;
        Bump(isInvocation ? "sites.invocation" : "sites.creation");

        var caller = FindCaller(node, model, outer: false);
        var callerType = caller?.sym.ContainingType ?? model.GetEnclosingSymbol(node.SpanStart)?.ContainingType;
        var si = model.GetSymbolInfo(node);
        var target = si.Symbol as IMethodSymbol;
        var def = target == null ? null : (target.ReducedFrom ?? target).OriginalDefinition;
        if (def?.PartialImplementationPart != null) def = def.PartialImplementationPart;
        bool own = def != null && (def.DeclaringSyntaxReferences.Any(r => ownTrees.Contains(r.SyntaxTree))
            || (def.MethodKind == MethodKind.Constructor && def.ContainingType.DeclaringSyntaxReferences.Any(r => ownTrees.Contains(r.SyntaxTree))));
        var cls = target != null ? Classify(node, model, target, callerType) : ("unresolved", "", "", "", "");

        ws.WriteLine(new JsonObject
        {
            ["file"] = Rel(tree.FilePath),
            ["line"] = Line(tree, node.SpanStart),
            ["name"] = SyntacticName(node),
            ["creation"] = isCreation,
            ["in_method"] = caller != null,
            ["caller"] = caller?.name,
            ["caller_kind"] = caller?.kind,
            ["status"] = si.Symbol == null ? "unresolved" : target == null ? "non_method" : target.MethodKind.ToString(),
            ["own"] = own,
            ["kind"] = cls.Item1,
            ["subkind"] = cls.Item2,
            ["receiver"] = cls.Item3,
            ["target_sig"] = def?.ToDisplayString(),
            ["target_name"] = def == null ? null : (def.MethodKind == MethodKind.Constructor ? def.ContainingType.Name : def.Name),
            ["target_type"] = def?.ContainingType?.Name,
            ["text"] = node.ToString().Length > 120 ? node.ToString()[..120] : node.ToString(),
        }.ToJsonString(jsonOpts));

        if (caller == null) { Bump("skip.not_in_method"); continue; }
        if (target == null || def == null)
        {
            Bump(si.Symbol == null ? (si.CandidateSymbols.Length > 0 ? "skip.unresolved_candidates:" + si.CandidateReason : "skip.unresolved") : "skip.non_method");
            continue;
        }
        if (target.MethodKind is MethodKind.DelegateInvoke) { Bump("skip.delegate_invoke"); continue; }
        if (target.MethodKind is MethodKind.LocalFunction) { Bump("skip.target_local_function"); continue; }
        if (!own) { Bump("skip.target_not_own_source"); continue; }

        var targetType = def.ContainingType;
        JsonObject? tgt = null; // null => implicit default ctor: target is the type itself (see target_type)
        var tref = def.DeclaringSyntaxReferences.FirstOrDefault(r => ownTrees.Contains(r.SyntaxTree));
        if (tref != null)
        {
            var tnode = tref.GetSyntax();
            string tname = def.MethodKind == MethodKind.Constructor ? targetType.Name : def.Name;
            string tkind = def.MethodKind == MethodKind.Constructor ? (tnode is TypeDeclarationSyntax ? "primary_ctor" : "ctor") : "method";
            tgt = DeclInfo(tnode, tname, tkind, targetType);
        }

        var (kind, sub, receiver, receiverText, rel) = cls;
        var outer = caller.Value.kind == "local_function" ? FindCaller(caller.Value.decl, model, outer: true) : null;
        var rec = new JsonObject
        {
            ["caller"] = DeclInfo(caller.Value.decl, caller.Value.name, caller.Value.kind, callerType),
            ["caller_outer"] = outer == null ? null : DeclInfo(outer.Value.decl, outer.Value.name, outer.Value.kind, outer.Value.sym.ContainingType),
            ["caller_type_decls"] = callerType == null ? null : TypeDecls(callerType),
            ["target"] = tgt,
            ["target_type"] = TypeDecls(targetType),
            ["target_type_name"] = targetType.Name,
            ["call_line"] = Line(tree, node.SpanStart),
            ["call_file"] = Rel(tree.FilePath),
            ["kind"] = kind,
            ["subkind"] = sub,
            ["receiver"] = receiver,
            ["receiver_text"] = receiverText,
            ["rel"] = rel,
            ["target_static"] = def.IsStatic,
            ["target_sig"] = def.ToDisplayString(),
            ["target_arity"] = def.Parameters.Length,
            ["target_type_kind"] = targetType.TypeKind.ToString(),
            ["call_text"] = node.ToString().Length > 120 ? node.ToString()[..120] : node.ToString(),
        };
        w.WriteLine(rec.ToJsonString(jsonOpts));
        Bump("kept." + kind);
    }
}
if (membersOut != null)
{
    using var wm = new StreamWriter(membersOut);
    void Emit(SyntaxNode site, SemanticModel model, ISymbol tsym, SyntaxNode? tdecl, string tname, string kind, JsonObject extra)
    {
        var caller = FindCaller(site, model, outer: false);
        if (caller == null) { Bump("m.skip.not_in_method"); return; }
        if (tdecl == null || !ownTrees.Contains(tdecl.SyntaxTree)) { Bump("m.skip.not_own"); return; }
        var callerType = caller.Value.sym.ContainingType;
        var targetType = tsym.ContainingType;
        var outer = caller.Value.kind == "local_function" ? FindCaller(caller.Value.decl, model, outer: true) : null;
        var rec = new JsonObject
        {
            ["caller"] = DeclInfo(caller.Value.decl, caller.Value.name, caller.Value.kind, callerType),
            ["caller_outer"] = outer == null ? null : DeclInfo(outer.Value.decl, outer.Value.name, outer.Value.kind, outer.Value.sym.ContainingType),
            ["caller_type_decls"] = callerType == null ? null : TypeDecls(callerType),
            ["target"] = DeclInfo(tdecl, tname, kind, targetType),
            ["target_type"] = TypeDecls(targetType),
            ["target_type_name"] = targetType.Name,
            ["call_line"] = Line(site.SyntaxTree, site.SpanStart),
            ["call_file"] = Rel(site.SyntaxTree.FilePath),
            ["kind"] = kind,
            ["subkind"] = "",
            ["receiver"] = "",
            ["receiver_text"] = "",
            ["rel"] = SymbolEqualityComparer.Default.Equals(targetType.OriginalDefinition, callerType?.OriginalDefinition) ? "same_type" : "other_type",
            ["target_static"] = tsym.IsStatic,
            ["target_sig"] = tsym.OriginalDefinition.ToDisplayString(),
            ["target_arity"] = tsym is IMethodSymbol ms ? ms.Parameters.Length : tsym is IPropertySymbol ps ? ps.Parameters.Length : 0,
            ["target_type_kind"] = targetType.TypeKind.ToString(),
            ["call_text"] = site.ToString().Length > 120 ? site.ToString()[..120] : site.ToString(),
        };
        foreach (var kv in extra) rec[kv.Key] = kv.Value?.DeepClone();
        wm.WriteLine(rec.ToJsonString(jsonOpts));
        Bump("m.kept." + kind);
    }
    SyntaxNode? DeclOf(ISymbol s) => s.OriginalDefinition.DeclaringSyntaxReferences.FirstOrDefault(r => ownTrees.Contains(r.SyntaxTree))?.GetSyntax();
    foreach (var tree in ownTrees.OrderBy(t => t.FilePath))
    {
        var model = compilation.GetSemanticModel(tree);
        var seenOps = new HashSet<(int, int, string)>();
        foreach (var node in tree.GetRoot().DescendantNodes())
        {
            if (node is ConstructorInitializerSyntax ci)
            {
                if (model.GetSymbolInfo(ci).Symbol is IMethodSymbol cm && DeclOf(cm) is { } cd)
                    Emit(ci, model, cm, cd, cm.ContainingType.Name, "ctor_init",
                         new JsonObject { ["init"] = ci.ThisOrBaseKeyword.Text, ["argc"] = ci.ArgumentList.Arguments.Count });
                continue;
            }
            if (node.Ancestors().Any(a => a is InvocationExpressionSyntax inv && inv.Expression is IdentifierNameSyntax { Identifier.Text: "nameof" })) continue;
            var op = model.GetOperation(node);
            if (op == null || !seenOps.Add((op.Syntax.SpanStart, op.Syntax.Span.Length, op.Kind.ToString()))) continue;
            switch (op)
            {
                case IPropertyReferenceOperation pr:
                {
                    var prop = pr.Property.OriginalDefinition;
                    if (prop.IsImplicitlyDeclared || DeclOf(prop) is not { } pd) break;
                    var parent = pr.Parent;
                    bool set = false, get = true;
                    if (parent is ISimpleAssignmentOperation sa && sa.Target == pr) { set = true; get = false; }
                    else if (parent is ICompoundAssignmentOperation ca && ca.Target == pr) set = true;
                    else if (parent is IIncrementOrDecrementOperation) set = true;
                    else if (parent is ICoalesceAssignmentOperation coa && coa.Target == pr) set = true;
                    bool auto = pd is PropertyDeclarationSyntax pds && pds.ExpressionBody == null
                        && pds.AccessorList != null && pds.AccessorList.Accessors.All(a => a.Body == null && a.ExpressionBody == null);
                    string baseKind = prop.IsIndexer ? "indexer" : "property";
                    string tname = prop.IsIndexer ? "this[]" : prop.Name;
                    var extra = new JsonObject { ["auto_property"] = auto, ["receiver_implicit"] = pr.Instance == null || pr.Instance.IsImplicit,
                        ["in_object_initializer"] = parent?.Parent is IObjectOrCollectionInitializerOperation };
                    if (get) Emit(pr.Syntax, model, prop, pd, tname, baseKind + "_get", extra);
                    if (set) Emit(pr.Syntax, model, prop, pd, tname, baseKind + "_set", extra);
                    break;
                }
                case IBinaryOperation { OperatorMethod: { } om }:
                case IUnaryOperation { OperatorMethod: { } om2 }:
                case ICompoundAssignmentOperation { OperatorMethod: { } om3 }:
                case IIncrementOrDecrementOperation { OperatorMethod: { } om4 }:
                {
                    var m = (op switch { IBinaryOperation b => b.OperatorMethod, IUnaryOperation u => u.OperatorMethod,
                        ICompoundAssignmentOperation c => c.OperatorMethod, IIncrementOrDecrementOperation i => i.OperatorMethod, _ => null })!.OriginalDefinition;
                    if (m.IsImplicitlyDeclared || DeclOf(m) is not { } md) break;
                    Emit(op.Syntax, model, m, md, md is OperatorDeclarationSyntax ods ? "operator " + ods.OperatorToken.Text : m.Name, "operator", new JsonObject());
                    break;
                }
                case IConversionOperation { OperatorMethod: { } cm2 } conv:
                {
                    var m = cm2.OriginalDefinition;
                    if (m.IsImplicitlyDeclared || DeclOf(m) is not { } md) break;
                    Emit(op.Syntax, model, m, md, md is ConversionOperatorDeclarationSyntax cds ? "operator " + cds.Type : m.Name, "conversion",
                         new JsonObject { ["implicit_in_source"] = conv.IsImplicit });
                    break;
                }
            }
        }
    }
}
foreach (var kv in stats.OrderBy(k => k.Key)) Console.Error.WriteLine($"[stat] {kv.Key} = {kv.Value}");
return errors.Count == 0 ? 0 : 1;

sealed class AnalyzerLoader : IAnalyzerAssemblyLoader
{
    public static readonly AnalyzerLoader Instance = new();
    public void AddDependencyLocation(string fullPath) { }
    public System.Reflection.Assembly LoadFromPath(string fullPath) => System.Reflection.Assembly.LoadFrom(fullPath);
}
