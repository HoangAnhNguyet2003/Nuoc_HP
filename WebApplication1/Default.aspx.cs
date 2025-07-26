using System;
using System.Collections.Generic;
using System.Data;
using System.Data.SqlClient;
using System.Linq;
using System.Web;
using System.Web.UI;
using System.Web.UI.WebControls;

namespace WebApplication1
{
    public partial class _Default : Page
    {
        protected void Page_Load(object sender, EventArgs e)
        {
            String strSql = "select * from tbl_DongHo;select * from tbl_model;";
            DataSet ds = Microsoft.ApplicationBlocks.Data.SqlHelper.ExecuteDataset(Utils.connectionString, CommandType.Text, strSql);


            DataTable dt = ds.Tables[0];
            string strHtml = "";
            for (int i = 0; i < dt.Rows.Count; i++)
            {
                strHtml += string.Format("<button onclick=\"selectMeter({0})\">{1}</button>", dt.Rows[i]["ID"].ToString(), dt.Rows[i]["Name"].ToString());
            }
            spDongHo.InnerHtml = strHtml;


            DataTable dt1 = ds.Tables[1];
            string strScript = "<script>";
            var strData = ConvertDataTabletoString(dt1);
            strScript += string.Format("var strData={0}", strData);
            strScript += "</script>";

            spSpan.InnerHtml = strScript;
            string ngayHtml = "<label for='daySelect'>Chọn ngày:</label>";
            ngayHtml += "<select id='daySelect' onchange ='onDateChange()'>";

            for (int i = 0; i <= 15; i++)
            {
                DateTime d = DateTime.Today.AddDays(-i);
                string val = d.ToString("dd/MM/yyyy");
                ngayHtml += $"<option value = '{val}'>{val}</option>";

            }
            ngayHtml += "</select>";
            spNgay.InnerHtml = ngayHtml;
        }

        public string ConvertDataTabletoString(DataTable dt)
        {
            System.Web.Script.Serialization.JavaScriptSerializer serializer = new System.Web.Script.Serialization.JavaScriptSerializer();
            List<Dictionary<string, object>> rows = new List<Dictionary<string, object>>();
            Dictionary<string, object> row;
            foreach (DataRow dr in dt.Rows)
            {
                row = new Dictionary<string, object>();
                foreach (DataColumn col in dt.Columns)
                {
                    row.Add(col.ColumnName, dr[col]);
                }
                rows.Add(row);
            }
            return serializer.Serialize(rows);
        }


    }
}



