/* NRB Projects — main.js */

// ── Mobile nav toggle ──────────────────────────────
const navToggle = document.getElementById("navToggle");
const navLinks = document.getElementById("navLinks");

if (navToggle && navLinks) {
    navToggle.addEventListener("click", () => {
        const open = navLinks.classList.toggle("open");
        navToggle.classList.toggle("open", open);
        navToggle.setAttribute("aria-expanded", open);
    });

    // Close nav on link click
    navLinks.querySelectorAll("a").forEach(link => {
        link.addEventListener("click", () => {
            navLinks.classList.remove("open");
            navToggle.classList.remove("open");
            navToggle.setAttribute("aria-expanded", false);
        });
    });
}

// ── Header scroll effect ───────────────────────────
const header = document.getElementById("site-header");
if (header) {
    const onScroll = () => {
        header.classList.toggle("scrolled", window.scrollY > 30);
    };
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
}

// ── Smooth scroll for anchor links ────────────────
function smoothScroll(event, targetId) {
    const el = document.getElementById(targetId);
    if (el) {
        event.preventDefault();
        const navH = parseInt(getComputedStyle(document.documentElement)
            .getPropertyValue("--nav-h")) || 72;
        const top = el.getBoundingClientRect().top + window.scrollY - navH - 24;
        window.scrollTo({ top, behavior: "smooth" });
    }
}

// ── Scroll-triggered reveal ────────────────────────
const revealEls = document.querySelectorAll(
    ".service-card, .project-card, .stat, .drone-video"
);
if (revealEls.length && "IntersectionObserver" in window) {
    const revealVariants = [
        "reveal-pop",
        "reveal-slide-left",
        "reveal-slide-right",
        "reveal-tilt",
        "reveal-soft-zoom"
    ];

    const obs = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
            if (entry.isIntersecting) {
                entry.target.classList.add("is-visible");
                obs.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1 });

    revealEls.forEach((el, i) => {
        el.classList.add("reveal-item");
        el.classList.add(revealVariants[i % revealVariants.length]);
        el.style.setProperty("--reveal-delay", `${(i % 6) * 70}ms`);
        obs.observe(el);
    });
}

// ── Ambient mouse-reactive background ───────────────
const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
if (!prefersReducedMotion) {
    const root = document.documentElement;
    let targetX = 50;
    let targetY = 25;
    let currentX = 50;
    let currentY = 25;

    const tickAmbient = () => {
        currentX += (targetX - currentX) * 0.06;
        currentY += (targetY - currentY) * 0.06;
        root.style.setProperty("--ambient-x", `${currentX.toFixed(2)}%`);
        root.style.setProperty("--ambient-y", `${currentY.toFixed(2)}%`);
        window.requestAnimationFrame(tickAmbient);
    };

    window.addEventListener("mousemove", (event) => {
        targetX = (event.clientX / window.innerWidth) * 100;
        targetY = (event.clientY / window.innerHeight) * 100;
    }, { passive: true });

    window.requestAnimationFrame(tickAmbient);
}

// ── Auto-dismiss flash messages ────────────────────
document.querySelectorAll(".flash").forEach(flash => {
    setTimeout(() => {
        flash.style.transition = "opacity 0.5s ease";
        flash.style.opacity = "0";
        setTimeout(() => flash.remove(), 500);
    }, 5000);
});

// ── Year in footer (fallback) ──────────────────────
document.querySelectorAll(".footer-year").forEach(el => {
    el.textContent = new Date().getFullYear();
});

// ── Hero video placeholder logic ────────────────────
const heroVideo = document.querySelector(".hero-video");
const heroVideoPlaceholder = document.getElementById("heroVideoPlaceholder");
if (heroVideo && heroVideoPlaceholder) {
    const hidePlaceholder = () => {
        heroVideoPlaceholder.style.display = "none";
    };

    heroVideo.addEventListener("playing", hidePlaceholder);
    heroVideo.addEventListener("canplay", hidePlaceholder);
}

// ── Simple pre-coded chatbot ────────────────────────
const chatbotTrigger = document.getElementById("chatbotTrigger");
const chatbotPanel = document.getElementById("chatbotPanel");
const chatbotClose = document.getElementById("chatbotClose");
const chatbotQuestions = document.getElementById("chatbotQuestions");
const chatbotMessages = document.getElementById("chatbotMessages");

const chatbotFaq = [
    {
        q: "What can NRB build?",
        a: "We deliver residential new builds, renovations, commercial fit-outs and civil works across Brisbane."
    },
    {
        q: "Where do you work?",
        a: "We service Greater Brisbane and nearby suburbs. Share your project location in the quote form and we can confirm quickly."
    },
    {
        q: "How fast are quotes?",
        a: "Most quote requests get a response within 1-2 business days depending on project scope."
    },
    {
        q: "How do I start?",
        a: "Use the Get a Quote page with your project details, budget, and timeline. We will contact you to plan the next step."
    }
];

if (chatbotTrigger && chatbotPanel && chatbotQuestions && chatbotMessages) {
    try {
        const pushMessage = (text, role, options = {}) => {
            const bubble = document.createElement("div");
            bubble.className = `chatbot-message chatbot-message--${role}`;
            if (options.typing) {
                bubble.classList.add("chatbot-message--typing");
            }
            bubble.textContent = text;
            chatbotMessages.appendChild(bubble);
            chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
            return bubble;
        };

        pushMessage(
            "Hi, I am NRB Assistant. Tap a question below and I will reply instantly.",
            "assistant"
        );

        chatbotFaq.forEach((item) => {
            const btn = document.createElement("button");
            btn.className = "chatbot-q-btn";
            btn.type = "button";
            btn.textContent = item.q;
            btn.addEventListener("click", () => {
                pushMessage(item.q, "user");
                const typingBubble = pushMessage("NRB Assistant is typing...", "assistant", { typing: true });

                window.setTimeout(() => {
                    if (typingBubble && typingBubble.parentNode) {
                        typingBubble.parentNode.removeChild(typingBubble);
                    }
                    pushMessage(item.a, "assistant");
                }, 420);
            });
            chatbotQuestions.appendChild(btn);
        });

        const setOpen = (open) => {
            chatbotPanel.classList.toggle("open", open);
            chatbotPanel.setAttribute("aria-hidden", String(!open));
            chatbotTrigger.setAttribute("aria-expanded", String(open));
        };

        chatbotTrigger.addEventListener("click", () => {
            setOpen(!chatbotPanel.classList.contains("open"));
        });

        if (chatbotClose) {
            chatbotClose.addEventListener("click", () => setOpen(false));
        }

        document.addEventListener("click", (event) => {
            const clickedInside = chatbotPanel.contains(event.target) || chatbotTrigger.contains(event.target);
            if (!clickedInside && chatbotPanel.classList.contains("open")) {
                setOpen(false);
            }
        });

        document.addEventListener("keydown", (event) => {
            if (event.key === "Escape" && chatbotPanel.classList.contains("open")) {
                setOpen(false);
            }
        });
    } catch (error) {
        console.error("Chatbot failed to initialize:", error);
    }
}