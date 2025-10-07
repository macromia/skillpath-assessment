import org.junit.Test;
import static org.junit.Assert.*;
import java.math.BigDecimal;
import java.util.*;

public class OrderTest {
    @Test
    public void testOrderTotal() {
        Order o = new Order("O1","C1","Books", new BigDecimal("12.50"), 4, "t");
        assertEquals(new BigDecimal("50.00"), o.total());
    }

    @Test
    public void testAggregateAndFilter() {
        List<Order> orders = Arrays.asList(
            new Order("O1","C1","A", new BigDecimal("50.0"),1,"t"),
            new Order("O2","C2","B", new BigDecimal("20.0"),3,"t"),
            new Order("O3","C3","A", new BigDecimal("60.0"),2,"t")
        );
        Map<String,Object> summary = OrderProcessor.aggregate(orders);
        assertEquals(150.00, (Double) summary.get("total_revenue"), 0.001);
        @SuppressWarnings("unchecked") Map<String, Long> perCat = (Map<String, Long>) summary.get("orders_per_category");
        assertEquals(Long.valueOf(2L), perCat.get("A"));
        List<Order> hv = OrderProcessor.filterHighValue(orders, new BigDecimal("100.0"));
        assertEquals(1, hv.size());
        assertEquals("O3", hv.get(0).getOrderId());
    }
}