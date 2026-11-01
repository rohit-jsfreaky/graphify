namespace Repro2;

public class Money
{
    private readonly decimal _v;

    public Money(decimal v)                       // constructor
    {
        _v = Check.Positive(v);
    }

    public decimal Rounded => Check.Round(_v);    // property getter

    public static explicit operator decimal(Money m) => Check.Half(m._v);   // conversion operator

    public decimal Doubled()                      // method with a local function
    {
        return Local();
        decimal Local() => Check.Twice(_v);
    }
}
