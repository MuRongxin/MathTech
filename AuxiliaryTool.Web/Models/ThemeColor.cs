using System;

namespace AuxiliaryTool.Web.Models
{
    public static class ThemeColor
    {
        static Random random = new Random();

        public static string RandomHexColor()
        {
            byte r = (byte)random.Next(256);
            byte g = (byte)random.Next(256);
            byte b = (byte)random.Next(256);
            return $"#{r:X2}{g:X2}{b:X2}";
        }
    }
}
