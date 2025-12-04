# Consensus Simulator

**Trường Đại học Sư phạm Kỹ thuật TP. Hồ Chí Minh**

**Khoa Công nghệ thông tin** 

**Giảng viên hướng dẫn:** TS. Huỳnh Xuân Phụng

**Nhóm thực hiện:** Nhóm 6

---

## Thành viên nhóm

| MSSV        | Họ tên                  |
| :---------- | :---------------------- |
| **2591302** | **Nguyễn Thanh Bình**   |
| **2591303** | **Huỳnh Đình Hiệp**     |
| **2591311** | **Lê Nguyễn Tuấn Kiệt** |
| **2591322** | **Trần Minh Sang**      |

---

## 1. Mô tả dự án

Dự án cung cấp 3 mô-đun Python độc lập mô phỏng các cơ chế đồng thuận phổ biến trong blockchain:

### **Proof of Work (pow_simulator.py)**
- Mô phỏng quá trình “đào” block bằng việc tìm nonce sao cho hàm băm SHA-256 thỏa mãn số lượng ký tự `0` đầu theo difficulty.
- Difficulty được điều chỉnh động dựa trên thời gian đào block tương tự Bitcoin.
- Nhiều miner cạnh tranh dựa trên thông số hash_power (tượng trưng cho sức mạnh tính toán).

### **Proof of Stake (pos_simulator.py)**
- Mô phỏng lựa chọn validator dựa trên phân phối stake.
- Xác suất validator được chọn tỷ lệ thuận với lượng coin họ nắm giữ.
- Tạo chuỗi block 30-slot và thống kê số lần mỗi validator được chọn.

### **Fork Resolution (fork_resolution.py)**
- Mô phỏng tình huống fork trong blockchain khi 2 block được tạo tại cùng một độ cao.
- Mỗi node trong mạng nhận block với độ trễ khác nhau → chọn nhánh khác nhau.
- Thuật toán **Longest Chain Rule** được áp dụng để xác định chuỗi chính (canonical chain).

## 2. Tính năng chính

### **Proof of Work**
- Nhiều miner chạy song song (có thể mở rộng bằng threading).
- Thuật toán đào thực tế dựa trên SHA-256 + difficulty.
- Difficulty adjustment → tăng hoặc giảm dựa trên block_time.
- Log chi tiết: miner thắng, thời gian đào, số attempts, hash đầu ra.

### **Proof of Stake**
- Lựa chọn validator bằng **Weighted Random Selection**.
- Stake lớn hơn → xác suất tạo block cao hơn.
- Dashboard thống kê xác suất thu được gần với lý thuyết.
- Chuỗi PoS tạo ra đầy đủ hash và timestamp.

### **Fork Resolution**
- Mô phỏng network latency → các node chọn nhánh khác nhau.
- Sinh block C2 và nối vào nhánh theo xác suất số node đang theo.
- Tính độ dài từng chain và chọn chain dài nhất.
- In ra chuỗi chính (canonical chain) sau khi giải fork.

### **Thiết kế dự án**
- Mỗi module chạy độc lập.
- Tương thích Python ≥ 3.8.