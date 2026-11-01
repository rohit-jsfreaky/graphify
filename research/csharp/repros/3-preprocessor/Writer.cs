namespace Repro3
{
    public class Writer
    {
        private readonly Buffer _buffer = new Buffer();
        private int _state;

        public int State
        {
            get
            {
                {
                    return _state;
                }
            }
        }

        public string Path
        {
            get
            {
                {
                    return "";
                }
            }
        }

        public void WriteValue(int typeCode)
        {
            {
                switch (typeCode)
                {
#if HAVE_DB_NULL
                    case 1:
                        break;
#endif
                }
            }
        }

        public void Flush()
        {
            Prepare();             // compiler: Writer.Flush -> Writer.Prepare
            _buffer.Append('x');   // compiler: Writer.Flush -> Buffer.Append
        }

        private void Prepare() { }
    }
}
