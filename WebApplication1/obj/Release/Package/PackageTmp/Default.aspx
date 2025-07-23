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
            min-width: 160px; /* Số này rộng bao nhiêu */
            width: 160px;
            font-weight: bold; /* In đậm các tên mô hình */
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
        document.addEventListener("DOMContentLoaded", function () {
            // Khai báo modelID nếu chưa có, ví dụ đây là mảng ID các mô hình
            let modelID = ["LSTM_MIN", "ISO_LATION", "MODEL3", "MODEL4"]; // Mảng mẫu các modelID

            // Hàm chuyển mô tả thành điểm số
            function TinhDiemKetLuan(txt) {
                if (!txt) return 0;
                txt = txt.trim().toLowerCase();
                if (txt.includes("thấp")) return 1;
                if (txt.includes("trung bình")) return 2;
                if (txt.includes("cao")) return 3;
                return 0;
            }

            let currentMeter = localStorage.getItem("currentMeter") || 1;

            function selectMeter(id) {
                currentMeter = id;
                localStorage.setItem("currentMeter", id);
                const meterName = meterNames[id];
                document.getElementById("selectedMeterName").innerText = "Đồng hồ: " + meterName;

                const selectedDate = document.getElementById("daySelect").value;
                const parts = selectedDate.split('/');
                const baseDate = new Date(parts[2], parts[1] - 1, parts[0]);

                let listDate = [];
                for (let i = 0; i < 7; i++) {
                    let d = new Date(baseDate);
                    d.setDate(d.getDate() - i);
                    let formatted = ("0" + d.getDate()).slice(-2) + "/" + ("0" + (d.getMonth() + 1)).slice(-2) + "/" + d.getFullYear();
                    document.getElementById("ngay" + (i + 1)).innerText = formatted;
                    listDate.push(formatted);
                }

                // Xóa sạch dữ liệu cũ trên bảng
                for (const id of modelID) {
                    for (let i = 0; i < 7; i++) {
                        const cell = document.querySelector(`#${id} td:nth-child(${i + 2})`);
                        if (cell) {
                            cell.innerText = "";
                            cell.className = "";
                        }
                    }
                }
                // Xóa dòng kết luận
                const tbody = document.querySelector('tbody[id$="tbodyContent"]');

                if (!tbody) {
                    console.error("Không tìm thấy tbodyContent trên DOM");
                    return;
                }
                const trList = tbody.querySelectorAll("tr");
                if (trList.length) {
                    for (let i = 0; i < 7; i++) {
                        const cell = trList[trList.length - 1].querySelector(`td:nth-child(${i + 2})`);
                        if (cell) cell.innerText = "";
                    }
                }

                const apiUrl = `http://localhost:5000/predict-batch?dong_ho=${encodeURIComponent(meterName)}&ngay=${selectedDate}`;
                fetch(apiUrl)
                    .then(res => res.json())
                    .then(data => {
                        console.log("Kết quả trả về từ API:", data);

                        data.forEach(item => {
                            const modelRowID = item.model.replace(/ /g, "_").toUpperCase();
                            const colIndex = listDate.indexOf(item.ngay);

                            if (colIndex !== -1) {
                                const cell = document.querySelector(`#${modelRowID} td:nth-child(${colIndex + 2})`);
                                if (cell) {
                                    cell.innerText = item.du_doan;
                                    const prediction = item.du_doan.trim().toLowerCase();

                                    if (prediction === "nghi ngờ cao") cell.className = "red";
                                    else if (prediction === "nghi ngờ trung bình") cell.className = "yellow";
                                    else if (prediction === "nghi ngờ thấp") cell.className = "green";
                                }
                            }
                        });

                        // Xử lý phần kết luận
                        let DuLieuNgay = {};
                        data.forEach(item => {
                            const ngay = item.ngay;
                            const model = item.model.replace(/ /g, "_").toUpperCase();
                            if (!DuLieuNgay[ngay]) DuLieuNgay[ngay] = {};
                            DuLieuNgay[ngay][model] = item.du_doan;
                        });

                        // Tính kết luận cho mỗi ngày
                        for (let i = 0; i < 7; i++) {
                            const ngay = listDate[i];
                            let tong = 0;
                            let count = 0;
                            modelID.forEach(model => {
                                let du_doan = (DuLieuNgay[ngay] && DuLieuNgay[ngay][model]) ? DuLieuNgay[ngay][model] : "";
                                let diem = TinhDiemKetLuan(du_doan);
                                tong += diem * 0.25;
                                if (diem > 0) count++;
                            });

                            let KetLuan = "";
                            if (count === 4) { // Đủ dữ liệu từ 4 mô hình
                                if (tong <= 1.5) KetLuan = "Nghi ngờ thấp";
                                else if (tong <= 2.5) KetLuan = "Nghi ngờ trung bình";
                                else KetLuan = "Nghi ngờ cao";
                            }

                            // Điền kết luận vào bảng
                            const tbody = document.querySelector('tbody[id$="tbodyContent"]');
                            const trList = tbody.querySelectorAll("tr");

                            if (trList.length) {
                                const cell = trList[trList.length - 1].querySelector(`td:nth-child(${i + 2})`);
                                if (cell) {
                                    cell.innerText = KetLuan;

                                    // Thêm class tương ứng với kết luận
                                    cell.classList.remove("ketluan-green", "ketluan-yellow", "ketluan-red");

                                    if (KetLuan === "Nghi ngờ thấp") cell.classList.add("ketluan-green");
                                    else if (KetLuan === "Nghi ngờ trung bình") cell.classList.add("ketluan-yellow");
                                    else if (KetLuan === "Nghi ngờ cao") cell.classList.add("ketluan-red");
                                }
                            }
                        }

                    })
                    .catch(err => {
                        console.error("Lỗi khi gọi API Flask:", err);
                    });
            }

            function onDateChange() {
                selectMeter(currentMeter);
            }

            const daySelect = document.getElementById("daySelect");
            if (daySelect) {
                daySelect.addEventListener("change", onDateChange);
                onDateChange(); // Gọi lần đầu
            }

            const searchInput = document.getElementById("searchMeter");
            const meterSelect = document.getElementById("meterSelect");

            if (meterSelect) {
                selectMeter(meterSelect.value);
            }

            if (searchInput && meterSelect) {
                const suggestionBox = document.getElementById("suggestion");

                function getMeterOptions() {
                    return Array.from(meterSelect.options).map(opt => ({
                        value: opt.value,
                        text: opt.text
                    }));
                }

                searchInput.addEventListener("input", function () {
                    const query = this.value.trim().toLowerCase();
                    suggestionBox.innerHTML = "";
                    if (!query) return;

                    const filtered = getMeterOptions().filter(option =>
                        option.text.toLowerCase().includes(query)
                    );

                    if (filtered.length === 0) {
                        suggestionBox.innerHTML = "<div style='color:gray;font-size:13px;padding:4px 8px;'>Không có kết quả</div>";
                        return;
                    }

                    filtered.forEach(option => {
                        const div = document.createElement("div");
                        div.style.padding = "5px 10px";
                        div.style.cursor = "pointer";
                        div.style.background = "#fff";
                        div.style.borderBottom = "1px solid #eee";
                        div.innerText = option.text;
                        div.addEventListener("mousedown", function () {
                            searchInput.value = option.text;
                            meterSelect.value = option.value;
                            selectMeter(option.value);
                            suggestionBox.innerHTML = "";
                        });
                        suggestionBox.appendChild(div);
                    });
                });

                document.addEventListener("click", function (e) {
                    if (e.target !== searchInput) suggestionBox.innerHTML = "";
                });
            }

            const freeDate = document.getElementById("freeDate");
            if (freeDate && daySelect) {
                freeDate.addEventListener("change", function () {
                    const val = this.value;
                    if (!val) return;

                    const d = new Date(val);
                    const ddmmyyyy = ("0" + d.getDate()).slice(-2) + "/" + ("0" + (d.getMonth() + 1)).slice(-2) + "/" + d.getFullYear();

                    let exists = false;
                    for (let opt of daySelect.options) {
                        if (opt.value === ddmmyyyy) {
                            exists = true;
                            break;
                        }
                    }

                    if (!exists) {
                        const newOption = document.createElement("option");
                        newOption.value = ddmmyyyy;
                        newOption.text = ddmmyyyy;
                        daySelect.insertBefore(newOption, daySelect.firstChild);
                    }

                    daySelect.value = ddmmyyyy;
                    onDateChange();
                });
            }
        });



    </script>

    <span id="spSpan" runat="server"></span>

</asp:Content>
