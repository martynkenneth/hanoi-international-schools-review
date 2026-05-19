const schools = [
  {
    name: "British International School Hanoi",
    curriculum: "English National Curriculum + IGCSE + IB",
    tuition: "$18,000 - $32,000 / year",
    district: "Long Bien",
    image:
      "https://images.unsplash.com/photo-1580582932707-520aed937b7b?auto=format&fit=crop&w=1200&q=60",
    fit: "Strong for UK pathway families seeking IB in senior years."
  },
  {
    name: "UNIS Hanoi",
    curriculum: "IB PYP/MYP/DP",
    tuition: "$15,000 - $35,000 / year",
    district: "Tay Ho",
    image:
      "https://images.unsplash.com/photo-1509062522246-3755977927d7?auto=format&fit=crop&w=1200&q=60",
    fit: "Excellent for globally mobile families and full IB continuity."
  },
  {
    name: "Concordia International School Hanoi",
    curriculum: "US Standards + AP",
    tuition: "$14,000 - $28,000 / year",
    district: "Tay Ho",
    image:
      "https://images.unsplash.com/photo-1588072432836-e10032774350?auto=format&fit=crop&w=1200&q=60",
    fit: "Good match for US curriculum with supportive ESL track."
  }
];

const offers = [
  {
    school: "British International School Hanoi",
    type: "Discount",
    title: "Early enrollment tuition discount",
    detail: "5% tuition reduction for applications completed before June 30, 2026.",
    deadline: "2026-06-30",
    verified: "Source-verified",
    source: "https://example.com/bis-hanoi-offers"
  },
  {
    school: "UNIS Hanoi",
    type: "Scholarship",
    title: "Merit scholarship for Grade 9 entry",
    detail: "Partial scholarship for high-performing students with leadership profile.",
    deadline: "2026-07-15",
    verified: "School-confirmed",
    source: "https://example.com/unis-scholarship"
  },
  {
    school: "Concordia International School Hanoi",
    type: "Waiver",
    title: "Application fee waiver week",
    detail: "Application fee waived for open day attendees registering onsite.",
    deadline: "2026-06-10",
    verified: "Self-reported",
    source: "https://example.com/concordia-social"
  }
];

function renderSchools() {
  const root = document.getElementById("schoolGrid");
  root.innerHTML = schools
    .map(
      (s) => `
    <article class="card">
      <img src="${s.image}" alt="${s.name} campus" loading="lazy" />
      <h3>${s.name}</h3>
      <p><strong>Curriculum:</strong> ${s.curriculum}</p>
      <p><strong>Tuition:</strong> ${s.tuition}</p>
      <p><strong>District:</strong> ${s.district}</p>
      <p><strong>Fit:</strong> ${s.fit}</p>
    </article>`
    )
    .join("");
}

function verificationBadge(status) {
  if (status === "School-confirmed" || status === "Source-verified") {
    return '<span class="badge badge-verified">Verified</span>';
  }
  return '<span class="badge badge-self">Self-reported</span>';
}

function renderOffers(type = "all") {
  const list = document.getElementById("offerList");
  const filtered = type === "all" ? offers : offers.filter((o) => o.type === type);

  list.innerHTML = filtered
    .map(
      (o) => `
      <article class="card offer">
        ${verificationBadge(o.verified)}<span class="badge">${o.type}</span>
        <h3>${o.title}</h3>
        <p><strong>School:</strong> ${o.school}</p>
        <p>${o.detail}</p>
        <p><strong>Deadline:</strong> ${o.deadline}</p>
        <p><strong>Status:</strong> ${o.verified}</p>
        <p><a href="${o.source}" target="_blank" rel="noopener">Source link</a></p>
      </article>
    `
    )
    .join("");
}

document.getElementById("offerTypeFilter").addEventListener("change", (e) => {
  renderOffers(e.target.value);
});

document.getElementById("leadForm").addEventListener("submit", (e) => {
  e.preventDefault();
  const form = e.target;
  const message = document.getElementById("formMessage");

  if (!form.checkValidity()) {
    message.textContent = "Please complete all fields.";
    message.style.color = "#b91c1c";
    return;
  }

  const data = Object.fromEntries(new FormData(form).entries());
  localStorage.setItem("lead_capture", JSON.stringify({ ...data, createdAt: new Date().toISOString() }));
  message.textContent = "Success! You now have access to the discount pages.";
  message.style.color = "#166534";
  form.reset();
});

renderSchools();
renderOffers();
