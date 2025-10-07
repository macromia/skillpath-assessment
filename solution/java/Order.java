import java.math.BigDecimal;

public class Order {
    private final String orderId;
    private final String customerId;
    private final String category;
    private final BigDecimal unitPrice;
    private final int quantity;
    private final String timestamp;

    public Order(String orderId, String customerId, String category,
                 BigDecimal unitPrice, int quantity, String timestamp) {
        this.orderId = orderId;
        this.customerId = customerId;
        this.category = category;
        this.unitPrice = unitPrice;
        this.quantity = quantity;
        this.timestamp = timestamp;
    }

    public String getOrderId() { return orderId; }
    public String getCustomerId() { return customerId; }
    public String getCategory() { return category; }
    public BigDecimal getUnitPrice() { return unitPrice; }
    public int getQuantity() { return quantity; }
    public String getTimestamp() { return timestamp; }

    public BigDecimal total() {
        return unitPrice.multiply(BigDecimal.valueOf(quantity)).setScale(2, BigDecimal.ROUND_HALF_UP);
    }
}