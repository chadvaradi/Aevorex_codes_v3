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
            alert("Kérjük, adjon meg egy érvényes e-mail címet.");
            submitBtn.disabled = false;
            return;
          }

          const originalText = submitBtn.textContent;
          submitBtn.textContent = "Küldés...";

          try {
            const res = await fetch("/api/brevo/subscribe", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ email, source: "consulting-hero-hu", website_company_field }),
            });

            if (res.status === 204) {
              // honeypot – csendben kilépünk, NINCS redirect és nincs alert
              return;
            }

            if (res.status === 429) {
              const retryAfter = res.headers.get("Retry-After");
              alert(`Túl sok kísérlet. Próbálja újra ${retryAfter ?? "néhány"} másodperc múlva.`);
              return;
            }

            if (res.ok) {
              alert("Sikeresen feliratkozott! Kérjük, ellenőrizze a bejövő leveleit a megerősítéshez.");
              form.reset();
            } else {
              alert("A feliratkozás sikertelen. Kérjük, próbálja újra.");
            }
          } catch (err) {
            console.error(err);
            alert("Hiba történt. Kérjük, próbálja újra.");
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
          placeholder="E-mail cím"
          className="border-border/10 bg-foreground/10 grow"
        />
        <Button variant="default" size="lg" type="submit">
          E-mail feliratkozás
        </Button>
      </form>
      <p className="text-muted-foreground text-xs">
        Induló ajánlat: 50% kedvezmény az első 10 partnerünknek, akik referenciaügyfélként csatlakoznak.
      </p>
    </>
  );
}
