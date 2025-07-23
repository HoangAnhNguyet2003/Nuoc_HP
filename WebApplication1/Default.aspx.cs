using System;
using System.Collections.Generic;
using System.IO;
using System.Net;
using System.Web.Script.Serialization;

namespace WebApplication1
{
    public partial class _Default : System.Web.UI.Page
    {
        private const string V = "http://127.0.0.1:5000/get-all-isolation-data";

        protected void Page_Load(object sender, EventArgs e)
        {
            if (!IsPostBack)
            {
                // 1. Lấy danh sách đồng hồ từ Flask API
                string apiUrl = "http://127.0.0.1:5000/get-all-watch-names";
                List<string> meters = GetListFromApi(apiUrl);

                // 2. HTML button cho từng đồng hồ (truyền đúng tên đồng hồ)
                string strHtml = "";
                foreach (var name in meters)
                {
                    // escape ký tự nháy đơn 
                    string safeName = name.Replace("'", "\\'");
                    strHtml += $"<button onclick=\"selectMeter('{safeName}')\">{name}</button>";
                }

                spDongHo.InnerHtml = strHtml;

                // 3. Lấy dữ liệu model LSTM
                string lstmUrl = "http://127.0.0.1:5000/get-all-lstm-data";
                string lstmJson = GetJsonFromApi(lstmUrl);

                // 4. Lấy dữ liệu model Isolation
                string isoUrl = V;
                string isoJson = GetJsonFromApi(isoUrl);

                // 5. Inject biến JavaScript cho lstmData và isoData 
                string strScript = "<script>";
                strScript += $"var lstmData = {lstmJson ?? "[]"};\n";
                strScript += $"var isoData = {isoJson ?? "[]"};\n";
                strScript += "</script>";
                spSpan.Text = strScript;

                // 6. Tạo danh sách ngày gần đây
                string ngayHtml = "<label for='daySelect'>Chọn ngày:</label>";
                ngayHtml += "<select id='daySelect' onchange ='onDateChange()'>";
                for (int i = 0; i <= 15; i++)
                {
                    DateTime d = DateTime.Today.AddDays(-i);
                    string val = d.ToString("dd/MM/yyyy");
                    ngayHtml += $"<option value='{val}'>{val}</option>";
                }
                ngayHtml += "</select>";
                spNgay.InnerHtml = ngayHtml;
            }
        }

        // Hàm gọi API trả về List<string>
        private List<string> GetListFromApi(string url)
        {
            var json = GetJsonFromApi(url);
            JavaScriptSerializer js = new JavaScriptSerializer();
            List<string> result = js.Deserialize<List<string>>(json);
            return result;
        }

        // Hàm gọi API trả về string
        private string GetJsonFromApi(string url)
        {
            try
            {
                HttpWebRequest request = (HttpWebRequest)WebRequest.Create(url);
                request.Method = "GET";
                using (HttpWebResponse response = (HttpWebResponse)request.GetResponse())
                using (StreamReader sr = new StreamReader(response.GetResponseStream()))
                {
                    return sr.ReadToEnd();
                }
            }
            catch (Exception ex)
            {

                return "[]";
            }
        }
    }
}