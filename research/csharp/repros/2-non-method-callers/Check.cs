namespace Repro2;

public static class Check
{
    public static decimal Positive(decimal v) => v < 0 ? 0 : v;
    public static decimal Round(decimal v) => decimal.Round(v, 2);
    public static decimal Half(decimal v) => v / 2;
    public static decimal Twice(decimal v) => v * 2;
}
