"use client";

import { Button } from "@/launch-ui-pro-2.3.3/ui/button";
import { Input } from "@/launch-ui-pro-2.3.3/ui/input";

export default function ConsultingForm() {
  return (
    <>
      <form 
        className="flex w-full max-w-[420px] gap-2"
        onSubmit={async (e) => {
          e.preventDefault();
          const form = e.currentTarget;
          const submitBtn = form.querySelector('button[type="submit"]') as HTMLButtonElement;
          const fd = new FormData(form);
          const email = (fd.get("email") as string) || "";
          const website_company_field = (fd.get("website_company_field") as string) || "";

          // Duplakattintás ellen
          if (submitBtn.disabled) return;
          submitBtn.disabled = true;

          // Kliens oldali email validáció
          if (!email || !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) {
            alert("Please enter a valid email address.");
            submitBtn.disabled = false;
            return;
          }

          const originalText = submitBtn.textContent;
          submitBtn.textContent = "Submitting...";

          try {
            const res = await fetch("/api/brevo/subscribe", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ email, source: "consulting-hero", website_company_field }),
            });

            if (res.status === 204) {
              // honeypot – csendben kilépünk, NINCS redirect és nincs alert
              return;
            }

            if (res.status === 429) {
              const retryAfter = res.headers.get("Retry-After");
              alert(`Too many attempts. Try again in ${retryAfter ?? "a few"} seconds.`);
              return;
            }

            if (res.ok) {
              alert("Successfully subscribed! Please check your inbox to confirm.");
              form.reset();
            } else {
              alert("Subscription failed. Please try again.");
            }
          } catch (err) {
            console.error(err);
            alert("An error occurred. Please try again.");
          } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = originalText;
          }
        }}
      >
        {/* Honeypot spam védelem */}
        <input
          name="website_company_field"
          tabIndex={-1}
          autoComplete="off"
          aria-hidden="true"
          style={{ display: "none" }}
        />
        <Input
          name="email"
          type="email"
          required
          autoComplete="email"
          placeholder="Email address"
          className="border-border/10 bg-foreground/10 grow"
        />
        <Button variant="default" size="lg" type="submit">
          Subscribe with email
        </Button>
      </form>
      <p className="text-muted-foreground text-xs">
        Founding offer: 50% discount for the first 10 clients who join as reference partners
      </p>
    </>
  );
}
