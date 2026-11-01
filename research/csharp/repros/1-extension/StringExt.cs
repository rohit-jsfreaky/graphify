namespace Repro1;

public static class StringExt
{
    public static string Shout(this string s) => s.ToUpperInvariant() + "!";
}
