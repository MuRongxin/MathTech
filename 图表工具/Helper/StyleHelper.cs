

using System.Windows.Media;

namespace 图表工具.Helper
{
    public class StyleHelper
    {
        /// <summary>
        /// 将#xxxxxx类型转换为SolidColorBrush
        /// </summary>
        /// <param name="_colorStr"></param>
        /// <returns></returns>
        public static SolidColorBrush ConvertToSolidColorBrush(string _colorStr)
        {
            return new SolidColorBrush(ConvertToColor(_colorStr));
        }

        /// <summary>
        /// 将#xxxxxx类型转换为Color
        /// </summary>
        /// <param name="_colorStr"></param>
        /// <returns></returns>
        public static Color ConvertToColor(string _colorStr)
        {
            return (Color)ColorConverter.ConvertFromString(_colorStr);
        }
    }
}
