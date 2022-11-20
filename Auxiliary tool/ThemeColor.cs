using System;
using System.Collections.Generic;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Auxiliary_tools
{
    public static class ThemeColor
    {
        static int color_1 = 0;
        static int color_2 = 0;
        static int color_3 = 0;

        static List<string> colors=new List<string>() { };
        static Random random = new Random();

        public static Color RandomColor()
        {
            color_1 = random.Next(256);
            color_2 = random.Next(256);
            color_3 = random.Next(256);
            string r_color = color_1.ToString("X2");
            string g_color = color_2.ToString("X2");
            string b_color = color_3.ToString("X2");

            return ColorTranslator.FromHtml("#" + r_color+g_color+b_color);
        }
    }
}
