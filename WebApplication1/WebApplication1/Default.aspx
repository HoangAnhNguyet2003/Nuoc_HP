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
                            <tr>
                                <td>LSTM_minflow</td>
                                <td id="LSTMmin1"></td>
                                <td id="LSTMmin2"></td>
                                <td id="LSTMmin3"></td>
                                <td id="LSTMmin4"></td>
                                <td id="LSTMmin5"></td>
                                <td id="LSTMmin6"></td>
                                <td id="LSTMmin7"></td>
                            </tr>
                            <tr>
                                <td>LSTM_maxflow</td>
                                <td id="LSTMmax1"></td>
                                <td id="LSTMmax2"></td>
                                <td id="LSTMmax3"></td>
                                <td id="LSTMmax4"></td>
                                <td id="LSTMmax5"></td>
                                <td id="LSTMmax6"></td>
                                <td id="LSTMmax7"></td>
                            </tr>

                            <tr>
                                <td>Isolation_minflow</td>
                                <td id="Isomin1"></td>
                                <td id="Isomin2"></td>
                                <td id="Isomin3"></td>
                                <td id="Isomin4"></td>
                                <td id="Isomin5"></td>
                                <td id="Isomin6"></td>
                                <td id="Isomin7"></td>
                            </tr>
                            <tr>
                                <td>Isolation_maxflow</td>
                                <td id="Isomax1"></td>
                                <td id="Isomax2"></td>
                                <td id="Isomax3"></td>
                                <td id="Isomax4"></td>
                                <td id="Isomax5"></td>
                                <td id="Isomax6"></td>
                                <td id="Isomax7"></td>
                            </tr>

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
        let modelID = ["LSTM_MIN", "ISO_LATION", "MODEL_3", "MODEL_4"];

        function selectMeter(name) {
            document.getElementById("selectedMeterName").innerText = "Đồng hồ: " + name;
            const date = document.getElementById('daySelect').value;
            showData(name, date);
        }

        function onDateChange() {
            const buttons = document.querySelectorAll("button[onclick^='selectMeter']");
            const activeButton = Array.from(buttons).find(btn => btn.classList.contains("active"));
            const name = activeButton ? activeButton.innerText : (lstmData.length > 0 ? lstmData[0].watch_name : "");
            const date = document.getElementById('daySelect').value;
            showData(name, date);
        }

        function parseDate(dateStr) {
            const parts = dateStr.split('/');
            return new Date(parts[2], parts[1] - 1, parts[0]);
        }

        function formatDate(date) {
            const day = String(date.getDate()).padStart(2, '0');
            const month = String(date.getMonth() + 1).padStart(2, '0');
            const year = date.getFullYear();
            return `${day}/${month}/${year}`;
        }

        function classifySuspicionLevel(differencePercentage) {
            if (differencePercentage < 2) {
                return "Nghi ngờ thấp";
            } else if (differencePercentage >= 2 && differencePercentage <= 5) {
                return "Nghi ngờ TB";
            } else if (differencePercentage >5){
                return "Nghi ngờ cao";
            }
        }

        function classifyIsolationSuspicion(minPred, maxPred) {
            if (minPred === 0 || maxPred === 0) {
                return "Nghi ngờ thấp";
            } else if (minPred === 1 || maxPred === 1) {
                return "Nghi ngờ cao";
            } else {
                return "Nghi ngờ không xác định";
            }
        }

        function showData(name, date) {
            const lstm = lstmData.find(x => x.watch_name === name && x.date === date);
            const iso = isoData.find(x => x.watch_name === name && x.date === date);
            let html = "";
            let formattedDate = date;

            if (lstmData && lstmData.length > 0) {
                const selectedDate = parseDate(date);

                for (let i = 0; i < 7; i++) {
                    const currentDate = new Date(selectedDate);
                    currentDate.setDate(currentDate.getDate() + i);
                    const formatted = formatDate(currentDate);

                    // Cập nhật cột ngày tương ứng (ngay1 -> ngay7)
                    const dayCell = document.getElementById(`ngay${i + 1}`);
                    if (dayCell) dayCell.innerText = formatted;

                    const lstmItem = lstmData.find(x => x.watch_name === name && x.date === formatted);

                    let minText = "Chưa có dữ liệu";
                    let maxText = "Chưa có dữ liệu";

                    if (lstmItem) {
                        const minPred = lstmItem.min_pred;
                        const minAvg = lstmItem.min_avg;
                        const maxPred = lstmItem.max_pred;
                        const maxAvg = lstmItem.max_avg;

                        let minDiff = 8; // Mặc định nghi ngờ TB
                        let maxDiff = 8;

                        if (minPred != null && minAvg != null && minAvg !== 0) {
                            minDiff = ((minAvg - minPred) / minAvg) * 100;
                        }

                        if (maxPred != null && maxAvg != null && maxAvg !== 0) {
                            maxDiff = ((maxAvg - maxPred) / maxAvg) * 100;
                        }

                        minText = classifySuspicionLevel(minDiff);
                        maxText = classifySuspicionLevel(maxDiff);
                    }

                    const minCell = document.getElementById(`LSTMmin${i + 1}`);
                    const maxCell = document.getElementById(`LSTMmax${i + 1}`);
                    if (minCell) minCell.innerText = minText;
                    if (maxCell) maxCell.innerText = maxText;
                }
            } else {
                // Không có dữ liệu → gán tất cả là "Chưa có dữ liệu"
                for (let i = 1; i <= 7; i++) {
                    const day = parseDate(date);
                    day.setDate(day.getDate() + i - 1);
                    document.getElementById(`ngay${i}`).innerText = formatDate(day);

                    const minCell = document.getElementById(`LSTMmin${i}`);
                    const maxCell = document.getElementById(`LSTMmax${i}`);
                    if (minCell) minCell.innerText = "Chưa có dữ liệu";
                    if (maxCell) maxCell.innerText = "Chưa có dữ liệu";
                }
            }

            if (isoData && isoData.length > 0) {
                const selectedDate = parseDate(date); 

                for (let i = 0; i < 7; i++) {
                    const currentDate = new Date(selectedDate);
                    currentDate.setDate(currentDate.getDate() + i);
                    const formatted = formatDate(currentDate);

                    const isoItem = isoData.find(x => x.watch_name === name && x.date === formatted);

                    let minText = "Chưa có dữ liệu";
                    let maxText = "Chưa có dữ liệu";

                    if (isoItem) {
                        const isoMinPred = isoItem.min_pred;
                        const isoMaxPred = isoItem.max_pred;

                        minText = isoMinPred === 0 ? "Nghi ngờ thấp" :
                            isoMinPred === 1 ? "Nghi ngờ cao" : "Không xác định";

                        maxText = isoMaxPred === 0 ? "Nghi ngờ thấp" :
                            isoMaxPred === 1 ? "Nghi ngờ cao" : "Không xác định";
                    }

                    // Gán giá trị cho từng cột (từ Isomin1 đến Isomin7, tương tự max)
                    const minCell = document.getElementById(`Isomin${i + 1}`);
                    const maxCell = document.getElementById(`Isomax${i + 1}`);
                    if (minCell) minCell.innerText = minText;
                    if (maxCell) maxCell.innerText = maxText;
                }
            } else {
                // Không có dữ liệu → gán tất cả là "Chưa có dữ liệu"
                for (let i = 1; i <= 7; i++) {
                    const minCell = document.getElementById(`Isomin${i}`);
                    const maxCell = document.getElementById(`Isomax${i}`);
                    if (minCell) minCell.innerText = "Chưa có dữ liệu";
                    if (maxCell) maxCell.innerText = "Chưa có dữ liệu";
                }
            }

            document.getElementById('dataDisplay').innerHTML = html;
        }

        document.addEventListener("DOMContentLoaded", function () {
            const daySelect = document.getElementById("daySelect");
            if (daySelect) {
                daySelect.addEventListener("change", onDateChange);
                onDateChange();
            }
        });
    </script>

</asp:Content>
