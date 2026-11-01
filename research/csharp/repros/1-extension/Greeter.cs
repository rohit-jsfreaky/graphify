namespace Repro1;

public class Greeter
{
    public string Greet(string name)
    {
        return name.Shout();            // extension call: compiler target StringExt.Shout
    }

    public string GreetStatic(string name)
    {
        return StringExt.Shout(name);   // same method, static-call spelling (control)
    }
}
