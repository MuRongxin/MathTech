using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace Auxiliary_tool
{
    public partial class RandomPanle : UserControl
    {
        public RandomPanle()
        {
            InitializeComponent();
        }

        private void RandomPanle_Load(object sender, EventArgs e)
        {
            
        }

        Random random = new Random();   
        private void randomTimer_Tick(object sender, EventArgs e)
        {
           int temp=random.Next(Auxiliarymethods.Instance.dataList_1.Count);
            resoultLabel.Text = Auxiliarymethods.Instance.dataList_1[temp];
        }

    }
}
