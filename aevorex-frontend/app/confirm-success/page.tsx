"use client";
import { Button } from "@/launch-ui-pro-2.3.3/ui/button";

export default function ConfirmSuccess() {
  return (
    <div className="min-h-screen flex items-center justify-center px-6">
      <div className="max-w-xl text-center space-y-6">
        <h1 className="text-4xl font-semibold">Subscription confirmed 🎉</h1>
        <p className="text-muted-foreground">
          Thanks for joining <strong>Aevorex Consulting</strong>.
          You&apos;ll start receiving tools, insights and strategies soon.
        </p>

        {/* Másodlagos, nem tolakodó CTA */}
        <div className="flex gap-3 justify-center">
          <Button variant="default" onClick={() => (window.location.href = "/")}>
            Back to home
          </Button>
          {/* Opcionális: ha mégis adnál lehetőséget foglalásra */}
          {/* <Button variant="outline" onClick={() => (window.location.href = process.env.NEXT_PUBLIC_CALENDLY_URL || "#calendar")}>
            Book a consultation
          </Button> */}
        </div>

        <p className="text-xs text-muted-foreground">
          Didn&apos;t expect this email? You can unsubscribe anytime from the footer of our emails.
        </p>
      </div>
    </div>
  );
}
