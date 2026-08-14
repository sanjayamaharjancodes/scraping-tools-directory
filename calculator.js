(function () {
  "use strict";

  const plans = [
    { name: "Hobby", price: 49, credits: 100000 },
    { name: "Startup", price: 149, credits: 1000000 },
    { name: "Business", price: 299, credits: 3000000 },
    { name: "Scaling", price: 475, credits: 5000000 },
    { name: "Professional", price: 975, credits: 10500000 },
    { name: "Advanced", price: 1975, credits: 21500000 }
  ];

  const requestsInput = document.getElementById("monthly-requests");
  const profileSelect = document.getElementById("request-profile");
  const customField = document.getElementById("custom-credit-field");
  const customInput = document.getElementById("credits-per-request");
  const error = document.getElementById("calculator-error");
  const estimatedCredits = document.getElementById("estimated-credits");
  const recommendedPlan = document.getElementById("recommended-plan");
  const recommendationDetail = document.getElementById("recommendation-detail");
  const formatter = new Intl.NumberFormat("en-US", { maximumFractionDigits: 2 });

  function update() {
    const isCustom = profileSelect.value === "custom";
    customField.hidden = !isCustom;

    const requests = Number(requestsInput.value);
    const creditsPerRequest = Number(isCustom ? customInput.value : profileSelect.value);

    if (!Number.isFinite(requests) || requests <= 0 || !Number.isFinite(creditsPerRequest) || creditsPerRequest <= 0) {
      error.textContent = "Enter positive numbers for requests and credits per request.";
      error.hidden = false;
      return;
    }

    error.hidden = true;
    const requiredCredits = Math.ceil(requests * creditsPerRequest);
    estimatedCredits.textContent = formatter.format(requiredCredits);

    if (requiredCredits <= 1000) {
      recommendedPlan.textContent = "Free account may cover this volume";
      recommendationDetail.textContent = "ScraperAPI currently publishes a 1,000-credit free allowance. Confirm current signup terms before relying on it.";
      return;
    }

    const plan = plans.find((candidate) => candidate.credits >= requiredCredits);
    if (!plan) {
      recommendedPlan.textContent = "Enterprise / custom pricing";
      recommendationDetail.textContent = `${formatter.format(requiredCredits)} credits exceeds the largest published self-serve allowance of 21,500,000 credits.`;
      return;
    }

    const headroom = plan.credits - requiredCredits;
    const utilization = Math.round((requiredCredits / plan.credits) * 100);
    recommendedPlan.textContent = `${plan.name} — $${formatter.format(plan.price)}/month`;
    recommendationDetail.textContent = `${formatter.format(plan.credits)} credits included; ${formatter.format(headroom)} credits of headroom (${utilization}% estimated utilization).`;
  }

  requestsInput.addEventListener("input", update);
  profileSelect.addEventListener("change", update);
  customInput.addEventListener("input", update);
  update();
}());
