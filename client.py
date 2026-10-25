import math, sys
sys.stdout.reconfigure(encoding='utf-8')

class AutonomousAbTestBayesianStoppingGuardClient:
    """
    Bayesian Beta-Binomial conjugate updater for CRO A/B testing.
    Calculates posterior conversion distributions, chance of variant beating control,
    expected loss E[Loss], and triggers statistical early stopping.
    """
    def __init__(self, alpha_prior=1.0, beta_prior=1.0):
        self.alpha_0 = alpha_prior
        self.beta_0 = beta_prior

    def compute_posterior(self, impressions, conversions):
        alpha = self.alpha_0 + conversions
        beta = self.beta_0 + (impressions - conversions)
        mean = alpha / float(alpha + beta)
        var = (alpha * beta) / float(((alpha + beta) ** 2) * (alpha + beta + 1))
        return alpha, beta, mean, math.sqrt(var)

    def monte_carlo_win_probability(self, a_alpha, a_beta, b_alpha, b_beta, num_samples=5000):
        # Numerical integration / fast pseudo-random sampling
        # Approximation using normal distributions when alpha, beta > 10
        mu_a = a_alpha / float(a_alpha + a_beta)
        std_a = math.sqrt((a_alpha * a_beta) / (((a_alpha + a_beta)**2) * (a_alpha + a_beta + 1)))
        
        mu_b = b_alpha / float(b_alpha + b_beta)
        std_b = math.sqrt((b_alpha * b_beta) / (((b_alpha + b_beta)**2) * (b_alpha + b_beta + 1)))

        # P(B > A) where B - A ~ N(mu_b - mu_a, std_a^2 + std_b^2)
        diff_mean = mu_b - mu_a
        diff_std = math.sqrt(std_a**2 + std_b**2)
        z = diff_mean / max(1e-6, diff_std)

        # Standard normal CDF approximation (Abramowitz and Stegun)
        def phi(x):
            return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))

        prob_b_beats_a = phi(z)
        # Expected loss of choosing B if A is actually better
        expected_loss = max(0.0, -diff_mean) * (1.0 - prob_b_beats_a)

        return round(prob_b_beats_a, 4), round(expected_loss, 6), round(diff_mean / max(1e-6, mu_a) * 100.0, 2)

    def evaluate_experiment(self, control_views, control_conv, variant_views, variant_conv, loss_threshold=0.0005):
        a_alpha, a_beta, a_mean, a_std = self.compute_posterior(control_views, control_conv)
        b_alpha, b_beta, b_mean, b_std = self.compute_posterior(variant_views, variant_conv)

        prob_win, exp_loss, relative_uplift = self.monte_carlo_win_probability(a_alpha, a_beta, b_alpha, b_beta)

        if prob_win >= 0.98 and exp_loss <= loss_threshold:
            decision = "STOP_EXPERIMENT_DECLARE_VARIANT_WINNER"
            reason = f"Variant has {prob_win*100:.1f}% win probability with near-zero expected loss ({exp_loss:.6f})"
        elif prob_win <= 0.05:
            decision = "STOP_EXPERIMENT_ABORT_VARIANT_LOSING"
            reason = f"Variant has only {prob_win*100:.1f}% chance of beating control"
        elif control_views + variant_views >= 20000:
            decision = "STOP_EXPERIMENT_INCONCLUSIVE_INSUFFICIENT_UPLIFT"
            reason = "Reached maximum sample threshold without statistically significant divergence"
        else:
            decision = "CONTINUE_EXPERIMENT_GATHERING_DATA"
            reason = f"Current win prob ({prob_win*100:.1f}%) still converging; expected loss={exp_loss:.6f}"

        return {
            "status": "success",
            "control_conversion_rate": round(a_mean, 4),
            "variant_conversion_rate": round(b_mean, 4),
            "relative_uplift_pct": relative_uplift,
            "probability_variant_beats_control": prob_win,
            "expected_loss": exp_loss,
            "recommended_decision": decision,
            "decision_rationale": reason
        }
