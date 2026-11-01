#!/usr/bin/env bash
# Build the 3 libraries (net8.0), dump csc args, build the Roslyn key tool, produce answer keys.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
CS="${CS_ROOT:-/home/user/cs}"
export PATH=/root/.dotnet:$PATH DOTNET_ROOT=/root/.dotnet DOTNET_CLI_TELEMETRY_OPTOUT=1 DOTNET_NOLOGO=1
export NBGV_GitEngine=Disabled   # Nerdbank.GitVersioning cannot compute versions in a shallow clone
T="$HERE/tools/dump-csc-args.targets"; RSP="$CS/_rsp"; KEY="$CS/_key"; mkdir -p "$RSP" "$KEY"
build() { (cd "$CS/$1" && dotnet build "$2" --no-incremental -f net8.0 -c Release -p:ProvideCommandLineArgs=true \
  -p:CustomAfterMicrosoftCommonTargets="$T" -p:CscDumpDir="$RSP" | tail -3); }
build Dapper Dapper/Dapper.csproj
build AutoMapper src/AutoMapper/AutoMapper.csproj
build Newtonsoft.Json Src/Newtonsoft.Json/Newtonsoft.Json.csproj
(cd "$HERE/tools/RoslynCallKey" && dotnet build -c Release | tail -2)
K="$HERE/tools/RoslynCallKey/bin/Release/net8.0/RoslynCallKey.dll"
dotnet "$K" "$RSP/Dapper.net8.0.rsp" "$CS/Dapper/Dapper" "$CS/Dapper" "$KEY/Dapper.jsonl"
dotnet "$K" "$RSP/AutoMapper.net8.0.rsp" "$CS/AutoMapper/src/AutoMapper" "$CS/AutoMapper" "$KEY/AutoMapper.jsonl"
dotnet "$K" "$RSP/Newtonsoft.Json.net8.0.rsp" "$CS/Newtonsoft.Json/Src/Newtonsoft.Json" "$CS/Newtonsoft.Json" "$KEY/Newtonsoft.Json.jsonl"
