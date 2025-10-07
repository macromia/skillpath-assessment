import java.io.*;
import java.math.BigDecimal;
import java.nio.file.*;
import java.util.*;
import java.util.stream.Collectors;

public class OrderProcessor {
    private static final String[] REQUIRED = new String[]{
            "order_id","customer_id","category","unit_price","quantity","timestamp"
    };

    public static void main(String[] args) {
        Map<String, String> argmap = parseArgs(args);
        String input = argmap.get("--input");
        if (input == null) {
            System.err.println("Missing --input");
            System.exit(1);
        }
        BigDecimal threshold = new BigDecimal(argmap.getOrDefault("--threshold", "100.0"));
        try {
            List<Order> orders = loadOrders(input);
            if (orders.isEmpty()) {
                System.err.println("No valid orders found.");
                System.exit(2);
            }
            Map<String, Object> summary = aggregate(orders);
            writeSummary("summary.json", summary);
            List<Order> hv = filterHighValue(orders, threshold);
            writeHighValueCsv("high_value_orders.csv", hv);
            System.out.println("Wrote summary.json and high_value_orders.csv");
        } catch (Exception e) {
            System.err.println("Error: " + e.getMessage());
            System.exit(1);
        }
    }

    static Map<String, String> parseArgs(String[] args) {
        Map<String, String> m = new HashMap<>();
        for (int i = 0; i < args.length; i++) {
            if (args[i].startsWith("--")) {
                String key = args[i];
                String val = (i + 1 < args.length && !args[i+1].startsWith("--")) ? args[++i] : "true";
                m.put(key, val);
            }
        }
        return m;
    }

    static List<Order> loadOrders(String path) throws Exception {
        List<Order> out = new ArrayList<>();
        try (BufferedReader br = Files.newBufferedReader(Paths.get(path))) {
            String header = br.readLine();
            if (header == null) throw new IllegalArgumentException("Empty file");
            String[] cols = header.split(",");
            Set<String> set = new HashSet<>(Arrays.asList(cols));
            for (String req : REQUIRED) if (!set.contains(req))
                throw new IllegalArgumentException("Missing columns: " + req);
            String line; int row = 1;
            while ((line = br.readLine()) != null) {
                row++;
                String[] parts = line.split(",");
                try {
                    Map<String, String> r = mapRow(cols, parts);
                    BigDecimal unitPrice = new BigDecimal(r.get("unit_price"));
                    int quantity = Integer.parseInt(r.get("quantity"));
                    out.add(new Order(
                            r.get("order_id"), r.get("customer_id"), r.get("category"),
                            unitPrice, quantity, r.get("timestamp")
                    ));
                } catch (Exception ex) {
                    // skip malformed row
                }
            }
        }
        return out;
    }

    static Map<String, String> mapRow(String[] cols, String[] parts) {
        Map<String, String> r = new HashMap<>();
        for (int i = 0; i < Math.min(cols.length, parts.length); i++) {
            r.put(cols[i], parts[i]);
        }
        return r;
    }

    static Map<String, Object> aggregate(List<Order> orders) {
        double totalRevenue = orders.stream()
                .map(o -> o.total())
                .mapToDouble(bd -> bd.doubleValue())
                .sum();
        totalRevenue = Math.round(totalRevenue * 100.0) / 100.0;
        double aov = orders.isEmpty() ? 0.0 : Math.round((totalRevenue / orders.size()) * 100.0) / 100.0;

        Map<String, Long> perCat = orders.stream()
                .collect(Collectors.groupingBy(Order::getCategory, Collectors.counting()));

        Map<String, Double> revenueByCat = new HashMap<>();
        for (Order o : orders) {
            revenueByCat.merge(o.getCategory(), o.total().doubleValue(), Double::sum);
        }
        String topCat = null;
        if (!revenueByCat.isEmpty()) {
            double max = revenueByCat.values().stream().mapToDouble(Double::doubleValue).max().orElse(0);
            List<String> candidates = revenueByCat.entrySet().stream()
                    .filter(e -> Math.abs(e.getValue() - max) < 1e-9)
                    .map(Map.Entry::getKey).sorted().collect(Collectors.toList());
            topCat = candidates.get(0);
        }
        Map<String, Object> summary = new LinkedHashMap<>();
        summary.put("total_revenue", round2(totalRevenue));
        summary.put("average_order_value", round2(aov));
        summary.put("orders_per_category", perCat);
        summary.put("top_category_by_revenue", topCat);
        return summary;
    }

    static double round2(double d) {
        return Math.round(d * 100.0) / 100.0;
    }

    static List<Order> filterHighValue(List<Order> orders, BigDecimal threshold) {
        return orders.stream()
                .filter(o -> o.total().compareTo(threshold) >= 0)
                .collect(Collectors.toList());
    }

    static void writeSummary(String path, Map<String, Object> summary) throws IOException {
        try (Writer w = new BufferedWriter(new FileWriter(path))) {
            w.write("{\n");
            int i = 0; int n = summary.size();
            for (Map.Entry<String, Object> e : summary.entrySet()) {
                w.write(String.format("  \"%s\": %s%s\n", e.getKey(), jsonValue(e.getValue()), (++i<n)?",":""));
            }
            w.write("}\n");
        }
    }

    static String jsonValue(Object v) {
        if (v == null) return "null";
        if (v instanceof String) return \"\" + v.toString().replace("\"", "\\\"") + \"\";
        if (v instanceof Number) return v.toString();
        if (v instanceof Map) {
            @SuppressWarnings("unchecked") Map<String, Object> m = (Map<String, Object>) v;
            StringBuilder sb = new StringBuilder("{");
            int i=0; int n=m.size();
            for (Map.Entry<String,Object> e : m.entrySet()) {
                sb.append("\""+e.getKey()+"\": "+jsonValue(e.getValue()));
                if (++i<n) sb.append(", ");
            }
            sb.append("}");
            return sb.toString();
        }
        if (v instanceof Iterable) {
            StringBuilder sb = new StringBuilder("[");
            Iterator<?> it = ((Iterable<?>) v).iterator();
            while (it.hasNext()) { sb.append(jsonValue(it.next())); if (it.hasNext()) sb.append(", "); }
            sb.append("]");
            return sb.toString();
        }
        return \"\" + v.toString() + \"\";
    }

    static void writeHighValueCsv(String path, List<Order> rows) throws IOException {
        try (BufferedWriter bw = Files.newBufferedWriter(Paths.get(path))) {
            bw.write(String.join(",", REQUIRED));
            bw.newLine();
            for (Order o : rows) {
                bw.write(String.format("%s,%s,%s,%.2f,%d,%s",
                        o.getOrderId(), o.getCustomerId(), o.getCategory(),
                        o.getUnitPrice(), o.getQuantity(), o.getTimestamp()));
                bw.newLine();
            }
        }
    }
}
