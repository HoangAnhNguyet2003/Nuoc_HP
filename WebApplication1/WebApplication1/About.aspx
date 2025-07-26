<%@ Page Title="About" Language="C#" MasterPageFile="~/Site.Master" AutoEventWireup="true" CodeBehind="About.aspx.cs" Inherits="WebApplication1.About" %>

<asp:Content ID="BodyContent" ContentPlaceHolderID="MainContent" runat="server">
    <main aria-labelledby="title">
        <h2 id="title">Hướng dẫn sử dụng hệ thống dự đoán rò rỉ nước bằng Trí tuệ nhân tạo</h2>

        <h3 class="text-center">Giới thiệu</h3>
        <p>
            Hệ thống được phát triển nhằm hỗ trợ phát hiện sớm rò rỉ nước trên các đồng hồ đo lưu lượng bằng cách ứng dụng các mô hình Trí tuệ nhân tạo (AI) như LSTM và Isolation Forest.
        </p>

        <h3>Chức năng chính</h3>
        <ul>
            <li>Hiển thị dữ liệu dự đoán tình trạng rò rỉ theo từng ngày</li>
            <li>Cho phép chọn đồng hồ cần theo dõi</li>
            <li>Phân tích và cảnh báo với 3 mức độ nghi ngờ: <strong>Nghi ngờ thấp</strong>, <strong>Nghi ngờ trung bình</strong>, và <strong>Nghi ngờ cao</strong></li>
        </ul>

        <h3>Cách sử dụng</h3>
        <ol>
            <li>Chọn đồng hồ cần theo dõi ở cột bên trái.</li>
            <li>Chọn ngày cần xem dữ liệu ở phần "Chọn ngày".</li>
            <li>Hệ thống sẽ tự động gửi truy vấn đến mô hình AI và hiển thị kết quả dự đoán của 7 ngày gần nhất trên bảng.</li>
            <li>Mỗi mô hình (LSTM và ISO_FOREST) sẽ dự đoán riêng biệt. Các mức dự đoán sẽ được hiển thị theo màu sắc như sau:
            </li>
        </ol>

        <ul>
            <li><span style="color: #f44336; font-weight: bold;">Nghi ngờ cao (màu đỏ):</span> Có khả năng rò rỉ lớn</li>
            <li><span style="color: #ff9800; font-weight: bold;">Nghi ngờ trung bình (màu vàng):</span> Có dấu hiệu bất thường</li>
            <li><span style="color: #4caf50; font-weight: bold;">Nghi ngờ thấp (màu xanh):</span> Hoạt động bình thường</li>
        </ul>

        <h3>Lưu ý</h3>
        <p>
            Hệ thống chỉ mang tính chất hỗ trợ phân tích. Các dự đoán cần được xác minh thực tế bởi nhân viên kỹ thuật trước khi đưa ra hành động can thiệp.
        </p>

        <h3>Thông tin liên hệ</h3>
        <p>
            Mọi góp ý hoặc yêu cầu hỗ trợ, vui lòng liên hệ bộ phận kỹ thuật qua email:
            <a href="mailto:abc@huce.edu.vn">abc@huce.edu.vn</a>
        </p>
    </main>
</asp:Content>
