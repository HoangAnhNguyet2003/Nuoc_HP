<%@ Page Title="Quản lý đồng hồ nước" Language="C#" MasterPageFile="~/Site.Master" AutoEventWireup="true" CodeBehind="Default.aspx.cs" Inherits="WebApplication1._Default" %>

<asp:Content ID="BodyContent" ContentPlaceHolderID="MainContent" runat="server">

    <style>
        * {
            box-sizing: border-box;
            font-family: Arial;
        }

        .sidebar {
            width: 200px;
            background: #f1f1f1;
            padding: 20px;
            border-right: 2px solid #ccc;
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
            margin-bottom: 30px;
        }

        th,
        td {
            border: 1px solid #999;
            text-align: center;
            padding: 8px;
        }

        .red {
            background-color: #f44336;
            color: white;
        }

        .yellow {
            background-color: #ffeb3b;
        }

        .green {
            background-color: #4caf50;
            color: white;
        }

        .chart-container {
            width: 600px;
            margin: 0 auto 20px;
        }

        .legend {
            text-align: center;
            margin-top: 10px;
            font-size: 14px;
        }

            .legend span {
                display: inline-block;
                width: 14px;
                height: 14px;
                margin-right: 5px;
                vertical-align: middle;
            }

        select {
            padding: 5px;
            margin-bottom: 10px;
        }
    </style>

    <div class="row">
        <div class="col-sm-2">
            <div class="sidebar">
                <h2>Đồng hồ</h2>
                <span runat="server" id="spDongHo">
                    <button onclick="selectMeter(1)">Số 1</button>

                    <button onclick="selectMeter(2)">Số 2</button>
                    <button onclick="selectMeter(3)">Số 3</button>
                </span>

                <br>
                <br>
                <span id="spNgay" runat="server"></span>

            </div>
        </div>
        <div class="col-sm-10">
            <div class="content">
                <div id="divContent">
                    <table>
                        <thead>
                            <tr>
                                <th rowspan="2">MÔ HÌNH DỰ ĐOÁN</th>
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

                        <tbody id="tbodyContent">
                            <tr>
                                <td>modelName1</td>
                                <td class=""></td>
                                <td class=""></td>
                                <td class=""></td>
                                <td class=""></td>
                                <td class=""></td>
                                <td class=""></td>
                            </tr>
                        </tbody>

                    </table>
                </div>

                <div class="legend">
                    <span style="background: #f44336"></span>Rò rỉ (Đỏ) &nbsp;&nbsp;
       <span style="background: #ffeb3b"></span>Nghi ngờ (Vàng) &nbsp;&nbsp;
       <span style="background: #4caf50"></span>Không rò rỉ (Xanh)
                </div>

            </div>
        </div>
    </div>

    <span runat="server" id="spSpan"></span>

    <script>

        var objData = eval(strData);
        var strHtml = '';
        $.each(objData, function (index, value) {
            //alert(value["Name"]);
            strHtml += '<tr>';
            strHtml += '<td>' + value["Name"] + '</td>';
            strHtml += '<td class="" id="tdLSTM"></td>';
            strHtml += '<td class=""></td>';
            strHtml += '<td class=""></td>';
            strHtml += '<td class=""></td>';
            strHtml += '<td class=""></td>';
            strHtml += '<td class=""></td>'; strHtml += '<td class=""></td>';
            strHtml += '</tr>';
        });
        $('#tbodyContent').html(strHtml);


        $.get("http://localhost:5000/predict-batch", function (data) {
            alert('hi');
            $("#tdLSTM").html(data[0]);

        });

        let currentMeter = 1;

        function onDateChange() {
            selectMeter(currentMeter);
        }

        function selectMeter(id) {

        }

        selectMeter(1);

        window.onload = function () {
            const selector = document.getElementById("daySelect");
            if (selector) {
                document.getElementById("daySelect").addEventListener("change", CapNhatNgay);
                CapNhatNgay();
            }
            else {
                console.error("Không tìm thấy 'daySelect'");
            }
        };

        function CapNhatNgay() {
            var selectDate = document.getElementById("daySelect").value;
            var parts = selectDate.split('/');
            var date = new Date(parts[2], parts[1] - 1, parts[0]);

            for (let i = 0; i < 7; i++) {
                let d = new Date(date);
                d.setDate(d.getDate() - i);
                let formatted = ("0" + d.getDate()).slice(-2) + "/" + ("0" + (d.getMonth() + 1)).slice(-2) + "/" + d.getFullYear();
                document.getElementById("ngay" + (i + 1)).innerText = formatted;
            }
        }


    </script>


</asp:Content>
