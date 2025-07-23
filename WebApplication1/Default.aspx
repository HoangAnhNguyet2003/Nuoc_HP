<%@ Page Title="Quản lý đồng hồ nước" Language="C#" MasterPageFile="~/Site.Master" AutoEventWireup="true" CodeBehind="Default.aspx.cs" Inherits="WebApplication1._Default" %>

<asp:Content ID="BodyContent" ContentPlaceHolderID="MainContent" runat="server">

    <style>
        .sidebar {
            width: 250px;
            background: #b8d6e6;
            padding: 20px;
            border-right: 2px solid rgb(252, 237, 237);
        }

            .sidebar h2 {
                margin-top: 0;
            }

            .sidebar button {
                width: 100%;
                margin: 10px 0;
                padding: 10px;
                cursor: pointer;
            }

        .content {
            flex: 1;
            padding: 20px;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 42px;
        }

        th, td {
            border: 2px solid #19304c;
            text-align: center;
            padding: 10px;
            font-size: 19px
        }


        .tracking-container {
            background-color: #b8dcff;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 0 8px rgba(0, 0, 0,0.1);
            font-size: 19px;
            font-weight: bold;
        }

            .tracking-container label {
                margin-bottom: 5px;
                display: inline-block;
            }

        .tracking-title {
            text-align: center;
            font-size: 25px;
            font-weight: bold;
            margin-bottom: 15px;
            color: #003366;
        }

        .tracking-input {
            display: flex;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 15px;
        }

        .input-group {
            display: flex;
            flex-direction: column;
            flex: 1 1 31%;
            min-width: 180px;
        }

        #searchMeter, #freeDate {
            width: 100%;
        }

        .ketluan-green {
            color: #0d8527; /* Xanh lá cây */
            background: #e8fbe8 !important; /* Nền xanh lá pha trắng */
            font-weight: bold;
        }

        .ketluan-yellow {
            color: #8d7d04; /* Vàng */
            background: #fffde3 !important; /* Nền vàng pha trắng */
            font-weight: bold;
        }

        .ketluan-red {
            color: #b91828; /* Đỏ */
            background: #ffeaea !important; /* Nền đỏ pha trắng */
            font-weight: bold;
        }

        .red {
            background-color: white;
            font-weight: bold;
            color: #ee3f32;
        }

        .yellow {
            background-color: white;
            color: #b6a829;
            font-weight: bold;
        }

        .green {
            background-color: white;
            color: #4caf50;
            font-weight: bold;
        }

        .dongho-title {
            font-size: 16px;
            font-weight: bold;
        }


        select {
            padding: 5px;
            margin-bottom: 10px;
        }

        th:first-child,
        td:first-child {
            min-width: 160px; /* Số này rộng */
            width: 160px;
            font-weight: bold; /* In đậm các tên mô hình AI */
        }


        @media (max-width: 1199px) {
            .tracking-container, .content {
                max-width: 96vw;
            }

            table, th, td {
                font-size: 16px;
            }

            h3#selectedMeterName, .tracking-title {
                font-size: 22px;
            }
        }

        @media (max-width: 900px) {
            .tracking-container, .content {
                max-width: 100vw;
            }

            table, th, td {
                font-size: 14.5px;
            }
        }

        @media (max-width: 768px) {
            .tracking-input {
                flex-direction: column;
                gap: 13px;
            }

            .input-group {
                min-width: 100px;
                width: 100%;
                flex: 1 1 100%;
            }

            table th, table td {
                font-size: 13.5px;
                padding: 8px 3px;
            }

            .content, .tracking-container, .chu_thich {
                max-width: 100vw;
                padding: 8px 3vw;
            }

            h3#selectedMeterName, .tracking-title {
                font-size: 17px;
            }
        }

        @media (max-width: 600px) {
            .tracking-container, .content, .chu_thich {
                padding: 4px 2vw;
                max-width: 100vw;
            }

            .tracking-title, h3#selectedMeterName {
                font-size: 14.5px;
            }

            table {
                font-size: 11px !important;
                border-radius: 0;
            }

                table th, table td {
                    padding: 3px 2px !important;
                    min-width: 74px;
                    white-space: nowrap;
                }
        }

        @media (max-width: 500px) {
            .tracking-container, .content, .chu_thich {
                padding: 2px 1vw;
                font-size: 13px;
            }

            table th, table td {
                font-size: 10.5px !important;
                min-width: 60px;
            }
        }

        /* Đảm bảo bảng có thể kéo ngang trên mobile */
        table {
            overflow-x: auto;
            -webkit-overflow-scrolling: touch;
            background: #fff;
            border-radius: 8px;
        }

        /* Đảm bảo phần chọn ngày, đồng hồ không bị dính nhau trên mobile */
        .tracking-input {
            flex-wrap: wrap;
            gap: 12px;
            margin-bottom: 10px;
        }

        .input-group {
            margin-bottom: 0 !important;
        }

        /* Căn chỉnh container cho mobile/tablet cho gọn */
        .tracking-container {
            margin-left: auto;
            margin-right: auto;
            width: 100%;
            max-width: 1000px;
            box-sizing: border-box;
        }

        /* Fix cho suggestion (nếu dùng) trên mobile */
        #suggestion {
            flex-wrap: wrap;
            gap: 6px;
            font-size: 12px;
        }



        .chu_thich {
            font-size: 19px;
            color: #444;
            background-color: #f6fafd;
            border-left: 4px solid #299bd6;
            padding: 12px 18px;
            margin: 32px 0 0 0;
            border-radius: 6px;
            box-shadow: 0 1px 6px rgba(41, 155, 214, 0.08);
        }

            .chu_thich ul {
                margin: 10px 0 0 18px;
                padding-left: 0;
            }

            .chu_thich li {
                margin-bottom: 7px;
                line-height: 1.7;
            }

            .chu_thich b {
                color: #1a70ad;
                font-weight: 600;
            }

            .chu_thich .ketluan-green {
                color: #0d8527 !important;
                background: none !important;
                font-weight: bold !important;
            }

            .chu_thich .ketluan-yellow {
                color: #8d7d04 !important;
                background: none !important;
                font-weight: bold !important;
            }

            .chu_thich .ketluan-red {
                color: #b91828 !important;
                background: none !important;
                font-weight: bold !important;
            }

        .center-content {
            display: flex;
            flex-direction: column;
            align-items: center; /* Căn giữa theo chiều ngang */
            width: 100%;
        }

        .tracking-container, .content, .chu_thich {
            max-width: 900px;
            margin-left: auto;
            margin-right: auto;
            width: 100%;
        }
    </style>


    <asp:Literal ID="spSpan" runat="server" />

    <div class="center-content">
        <!-- Bảng theo dõi  -->
        <div class="tracking-container">
            <h3 class="tracking-title">Bảng theo dõi đồng hồ</h3>

            <div class="tracking-input">
                <!-- Cột 1: Chọn đồng hồ -->
                <div class="input-group">
                    <span runat="server" id="spDongHo"></span>
                </div>

                <!-- Cột 2: Chọn ngày -->
                <div class="input-group">
                    <span runat="server" id="spNgay"></span>
                </div>

                <!-- Cột 3: Search + Ngày tự do -->
                <div class="input-group">
                    <input type="text" id="searchMeter" placeholder="Tìm đồng hồ" style="padding: 5px; margin-bottom: 10px;">
                    <div id="suggestion" style="display: flex; flex-wrap; gap: 10px; margin-top: 5px"></div>
                    <input type="date" id="freeDate" lang="vi" placeholder="dd/mm/yyyy" style="padding: 5px;">
                </div>
            </div>
        </div>

        <!-- Bảng dự đoán -->
        <div class="col-sm-12">
            <div class="content" style="max-width: 1000px; margin: auto;">
                <h3 id="selectedMeterName" style="text-align: center; font-weight: bold; color: #0d47a1;">Đồng hồ: Văn Đẩu 8
                </h3>

                <table>
                    <thead>
                        <tr>
                            <th rowspan="5">MÔ HÌNH DỰ ĐOÁN</th>
                            <th colspan="7">DỰ ĐOÁN CÁC NGÀY</th>
                        </tr>
                        <tr>
                            <th id="ngay1">Ngày 1</th>
                            <th id="ngay2">Ngày 2</th>
                            <th id="ngay3">Ngày 3</th>
                            <th id="ngay4">Ngày 4</th>
                            <th id="ngay5">Ngày 5</th>
                            <th id="ngay6">Ngày 6</th>
                            <th id="ngay7">Ngày 7</th>
                        </tr>
                    </thead>
                    <tbody id="tbodyContent" runat="server">
                        <%-- AutoCompleteType generate by C# in .cs Day la bang du doan  --%>
                    </tbody>
                </table>
                <div id="dataDisplay"></div>
                <!-- THÊM THẺ NÀY ĐỂ HIỂN THỊ KẾT QUẢ -->

                <!-- Chú thích bên dưới bảng dự đoán -->
                <div class="chu_thich">
                    <b>Giải thích về cách xác định mức độ nghi ngờ:</b>
                    <ul style="margin: 10px 0 0 18px;">
                        <li>Tổng hệ số tin tưởng của 4 mô hình bằng 1, mỗi mô hình đóng góp 0.25.
                        </li>
                        <li>Chấm điểm từng mô hình:<br>
                            &nbsp;&nbsp;Nghi ngờ thấp: 1 điểm &nbsp; | &nbsp; Nghi ngờ trung bình: 2 điểm &nbsp; | &nbsp; Nghi ngờ cao: 3 điểm
                        </li>
                        <li>Phần kết luận:<br>
                            - Cộng tổng điểm 4 mô hình (đã nhân hệ số 0.25).<br>
                            - <span class="ketluan-green">Nghi ngờ thấp:</span> 1 - 1.5 điểm<br>
                            - <span class="ketluan-yellow">Trung bình:</span> 1.51 - 2.5 điểm<br>
                            - <span class="ketluan-red">Cao:</span> 2.51 - 3 điểm
                        </li>
                    </ul>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Khai báo modelID 
        let modelID = ["LSTM_MIN", "ISO_LATION", "MODEL_3", "MODEL_4"];

        // Hàm chuyển mô tả thành điểm số
        

        // Xử lý chọn đồng hồ
        function selectMeter(name) {
            document.getElementById("selectedMeterName").innerText = "Đồng hồ: " + name;
            var date = document.getElementById('daySelect').value;
            showData(name, date);
        }

        // Xử lý đổi ngày
        function onDateChange() {
            var buttons = document.querySelectorAll("button[onclick^='selectMeter']");
            var activeButton = Array.from(buttons).find(btn => btn.classList.contains("active"));
            var name = activeButton ? activeButton.innerText : (lstmData.length > 0 ? lstmData[0].watch_name : "");
            var date = document.getElementById('daySelect').value;
            showData(name, date);
        }

        // Hiển thị dữ liệu dự đoán ra bảng
        function showData(name, date) {
            var lstm = lstmData.find(x => x.watch_name === name && x.date === date);
            var iso = isoData.find(x => x.watch_name === name && x.date === date);

            var html = "";
            if (lstm) {
                html += "<h3>Kết quả LSTM</h3>";
                html += "<table border='1'><tr><th>Ngày</th><th>min_avg</th><th>min_pred</th><th>max_avg</th><th>max_pred</th></tr>";
                html += `<tr><td>${lstm.date}</td><td>${lstm.min_avg}</td><td>${lstm.min_pred}</td><td>${lstm.max_avg}</td><td>${lstm.max_pred}</td></tr>`;
                html += "</table>";
            }
            if (iso) {
                html += "<h3>Kết quả Isolation Forest</h3>";
                html += "<table border='1'><tr><th>Ngày</th><th>min_avg</th><th>min_pred</th><th>max_avg</th><th>max_pred</th></tr>";
                html += `<tr><td>${iso.date}</td><td>${iso.min_avg}</td><td>${iso.min_pred}</td><td>${iso.max_avg}</td><td>${iso.max_pred}</td></tr>`;
                html += "</table>";
            }
            if (!lstm && !iso) {
                html = "<p>Không có dữ liệu cho đồng hồ và ngày đã chọn.</p>";
            }
            document.getElementById('dataDisplay').innerHTML = html;
        }

        document.addEventListener("DOMContentLoaded", function () {
            // Gán sự kiện cho nút chọn ngày
            const daySelect = document.getElementById("daySelect");
            if (daySelect) {
                daySelect.addEventListener("change", onDateChange);
                onDateChange();
            }
        });
    </script>



</asp:Content>
