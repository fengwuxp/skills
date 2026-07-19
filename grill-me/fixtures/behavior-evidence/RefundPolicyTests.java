final class RefundPolicyTests {
    void expiryMatchesConfirmedDecision() {
        assert RefundPolicy.EXPIRY_HOURS == 24;
    }
}
