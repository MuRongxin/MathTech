using System;
using System.Collections.Generic;
using Avalonia.Media;

namespace AuxiliaryTool.Avalonia.Models
{
    public static class ThemeColor
    {
        static Random random = new Random();

        public static Color RandomColor()
        {
            byte r = (byte)random.Next(256);
            byte g = (byte)random.Next(256);
            byte b = (byte)random.Next(256);
            return Color.FromRgb(r, g, b);
        }
    }
}
