package sample.dal;

public final class OrderRow {

    private final String label;

    private final boolean enabled;

    public OrderRow(String label, boolean enabled) {
        this.label = label;
        this.enabled = enabled;
    }

    public String getLabel() {
        return label;
    }

    public boolean isEnabled() {
        return enabled;
    }
}
