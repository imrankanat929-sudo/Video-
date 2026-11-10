// Catalog + cart + WhatsApp/Telegram checkout.
// Builds a pre-filled order message and opens a chat with the store owner.
// All settings live in config.js.
(function () {
  "use strict";

  const cfg = window.STORE_CONFIG;
  const CART_KEY = "hh_cart_v1";
  const $ = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));

  const money = (n) => {
    const rounded = Math.round(n * 100) / 100;
    return cfg.currencySymbol + (Number.isInteger(rounded) ? rounded : rounded.toFixed(2));
  };
  const productById = (id) => cfg.products.find((p) => p.id === id);

  // ---------- Cart state (survives page reloads where storage is allowed) ----------
  let cart = [];
  try {
    cart = JSON.parse(localStorage.getItem(CART_KEY)) || [];
    cart = cart.filter((line) => productById(line.id));
  } catch (_) {
    cart = [];
  }
  const save = () => {
    try { localStorage.setItem(CART_KEY, JSON.stringify(cart)); } catch (_) { /* private mode */ }
  };

  function addToCart(id, color) {
    const line = cart.find((l) => l.id === id && l.color === color);
    if (line) line.qty += 1;
    else cart.push({ id, color, qty: 1 });
    save();
    render();
    toast(`${productById(id).name} (${color}) added`);
  }

  function changeQty(index, delta) {
    cart[index].qty += delta;
    if (cart[index].qty <= 0) cart.splice(index, 1);
    save();
    render();
  }

  function totals(initials) {
    const itemCount = cart.reduce((n, l) => n + l.qty, 0);
    const subtotal = cart.reduce((s, l) => s + productById(l.id).price * l.qty, 0);
    const initialsTotal = initials ? cfg.initialsPrice * itemCount : 0;
    const goods = subtotal + initialsTotal;
    const shipping = itemCount === 0 || goods >= cfg.freeShippingFrom ? 0 : cfg.flatShipping;
    return { itemCount, subtotal, initialsTotal, shipping, total: goods + shipping, goods };
  }

  // ---------- Catalog ----------
  function renderCatalog() {
    const grid = $("[data-catalog]");
    const tpl = $("#product-card");
    cfg.products.forEach((p) => {
      const card = tpl.content.firstElementChild.cloneNode(true);
      const img = $("[data-image]", card);
      img.src = p.image;
      img.alt = `${p.name} in ${p.colors[0].toLowerCase()} leather`;
      const badge = $("[data-badge]", card);
      if (p.badge) badge.textContent = p.badge; else badge.remove();
      $("[data-leather]", card).textContent = p.leather;
      $("[data-name]", card).textContent = p.name;
      $("[data-tagline]", card).textContent = p.tagline;
      $("[data-price]", card).textContent = money(p.price);
      const compare = $("[data-compare]", card);
      if (p.compareAt) compare.textContent = money(p.compareAt); else compare.remove();

      const colorsBox = $("[data-colors]", card);
      p.colors.forEach((color, i) => {
        const label = document.createElement("label");
        label.className =
          "cursor-pointer rounded-full border border-ink/15 px-3 py-1.5 text-xs font-medium transition " +
          "has-[:checked]:border-ink has-[:checked]:bg-ink has-[:checked]:text-cream";
        const input = document.createElement("input");
        input.type = "radio";
        input.name = `color-${p.id}`;
        input.value = color;
        input.className = "sr-only";
        input.checked = i === 0;
        label.append(input, document.createTextNode(color));
        colorsBox.append(label);
      });

      $("[data-add]", card).addEventListener("click", () => {
        const picked = $(`input[name="color-${p.id}"]:checked`, card);
        addToCart(p.id, picked ? picked.value : p.colors[0]);
      });
      grid.append(card);
    });
  }

  // ---------- Cart sheet ----------
  function render() {
    const form = $("[data-checkout]");
    const t = totals(form.initials.value.trim());
    $("[data-cart-count]").textContent = t.itemCount;

    const list = $("[data-cart-items]");
    list.replaceChildren();
    cart.forEach((line, i) => {
      const p = productById(line.id);
      const li = document.createElement("li");
      li.className = "flex items-center gap-3 rounded-2xl bg-white p-3";
      li.innerHTML = `
        <img class="h-16 w-16 shrink-0 rounded-xl object-cover" alt="" />
        <div class="min-w-0 flex-1">
          <p class="truncate font-semibold" data-n></p>
          <p class="text-xs text-ink/60" data-c></p>
          <p class="mt-1 text-sm font-semibold" data-p></p>
        </div>
        <div class="flex items-center gap-1">
          <button type="button" class="h-8 w-8 rounded-full border border-ink/15 text-lg leading-none" aria-label="Remove one" data-dec>−</button>
          <span class="w-6 text-center text-sm font-semibold" data-q></span>
          <button type="button" class="h-8 w-8 rounded-full border border-ink/15 text-lg leading-none" aria-label="Add one" data-inc>+</button>
        </div>`;
      $("img", li).src = p.image;
      $("[data-n]", li).textContent = p.name;
      $("[data-c]", li).textContent = line.color;
      $("[data-p]", li).textContent = money(p.price * line.qty);
      $("[data-q]", li).textContent = line.qty;
      $("[data-dec]", li).addEventListener("click", () => changeQty(i, -1));
      $("[data-inc]", li).addEventListener("click", () => changeQty(i, +1));
      list.append(li);
    });

    const empty = cart.length === 0;
    $("[data-cart-empty]").classList.toggle("hidden", !empty);
    form.classList.toggle("hidden", empty);

    $("[data-subtotal]").textContent = money(t.subtotal);
    $("[data-initials-total]").textContent = money(t.initialsTotal);
    $("[data-shipping]").textContent = t.shipping ? money(t.shipping) : "Free";
    $("[data-total]").textContent = money(t.total);
    const left = cfg.freeShippingFrom - t.goods;
    $("[data-free-hint]").textContent =
      !empty && left > 0 ? `Add ${money(left)} more for free shipping` : "";
  }

  const sheet = $("[data-sheet]");
  function openSheet() {
    sheet.classList.remove("hidden");
    document.body.style.overflow = "hidden";
  }
  function closeSheet() {
    sheet.classList.add("hidden");
    document.body.style.overflow = "";
  }

  // ---------- Order message + chat links ----------
  function orderId() {
    const d = new Date();
    const pad = (n) => String(n).padStart(2, "0");
    const rand = Math.random().toString(36).slice(2, 6).toUpperCase();
    return `HH-${pad(d.getMonth() + 1)}${pad(d.getDate())}-${rand}`;
  }

  function buildMessage(data) {
    const t = totals(data.initials);
    const lines = cart.map((l) => {
      const p = productById(l.id);
      return `• ${l.qty} × ${p.name} — ${l.color} (${money(p.price * l.qty)})`;
    });
    return [
      `Hi! New order ${orderId()} 🛍️`,
      "",
      ...lines,
      "",
      data.initials ? `Initials: ${data.initials.toUpperCase()} (+${money(t.initialsTotal)})` : null,
      `Shipping: ${t.shipping ? money(t.shipping) : "Free"}`,
      `TOTAL: ${money(t.total)}`,
      "",
      `Name: ${data.name}`,
      `City: ${data.city}`,
      `Delivery: ${data.delivery}`,
      data.note ? `Note: ${data.note}` : null,
      "",
      "Please send me the payment link 🙏",
    ]
      .filter((x) => x !== null)
      .join("\n");
  }

  // WhatsApp: https://wa.me/<number>?text=<message>
  const whatsappLink = (text) =>
    `https://wa.me/${cfg.whatsappNumber.replace(/\D/g, "")}?text=${encodeURIComponent(text)}`;
  // Telegram: https://t.me/<username>?text=<message> pre-fills the chat input.
  const telegramLink = (text) =>
    `https://t.me/${cfg.telegramUsername.replace(/^@/, "")}?text=${encodeURIComponent(text)}`;

  async function copy(text) {
    try { await navigator.clipboard.writeText(text); return true; } catch (_) { return false; }
  }

  function onSubmit(e) {
    e.preventDefault();
    const form = e.currentTarget;
    const channel = (e.submitter && e.submitter.dataset.channel) || "whatsapp";
    const data = Object.fromEntries(
      ["name", "city", "delivery", "initials", "note"].map((k) => [k, form[k].value.trim()])
    );
    const err = $("[data-form-error]");
    if (!data.name || !data.city) {
      err.textContent = "Please add your name and city so I can calculate shipping.";
      err.classList.remove("hidden");
      (data.name ? form.city : form.name).focus();
      return;
    }
    err.classList.add("hidden");

    const message = buildMessage(data);
    // Copy as a backup in case the chat app drops the pre-filled text.
    copy(message);
    const url = channel === "telegram" ? telegramLink(message) : whatsappLink(message);
    window.open(url, "_blank", "noopener");
    toast("Order copied & chat opened — just tap Send ✌️");
  }

  // ---------- Toast ----------
  let toastTimer;
  function toast(msg) {
    const el = $("[data-toast]");
    el.textContent = msg;
    el.classList.remove("translate-y-24", "opacity-0");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => el.classList.add("translate-y-24", "opacity-0"), 2400);
  }

  // ---------- Init ----------
  function init() {
    $$("[data-brand]").forEach((el) => (el.textContent = cfg.brandName));
    const hello = `Hi! I have a question about ${cfg.brandName} bags.`;
    $("[data-wa-direct]").href = whatsappLink(hello);
    $("[data-tg-direct]").href = telegramLink(hello);

    renderCatalog();
    $$("[data-open-cart]").forEach((b) => b.addEventListener("click", openSheet));
    $$("[data-close-cart]").forEach((b) => b.addEventListener("click", closeSheet));
    document.addEventListener("keydown", (e) => e.key === "Escape" && closeSheet());
    const form = $("[data-checkout]");
    form.addEventListener("submit", onSubmit);
    form.initials.addEventListener("input", render);
    render();
  }

  init();
})();
