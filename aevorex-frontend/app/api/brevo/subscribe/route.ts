import { NextResponse } from "next/server";
import { brevoBase, brevoHeaders } from "@/lib/brevo/client";
import { subscribeSchema } from "@/lib/brevo/validators";
import { clientKeyFromHeaders } from "@/lib/http";
import { rateLimit } from "@/lib/rate-limit";
import { hasMxRecord } from "@/lib/email";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function POST(req: Request) {
  try {
    // Rate limit
    const key = clientKeyFromHeaders(req.headers);
    const rl = rateLimit(key);
    if (!rl.ok) {
      return NextResponse.json(
        { error: "Too many requests. Please try again later." },
        { status: 429, headers: { "Retry-After": String(Math.ceil((rl.resetAt - Date.now()) / 1000)) } }
      );
    }

    const body = await req.json();
    const parse = subscribeSchema.safeParse(body);
    if (!parse.success) {
      return NextResponse.json({ error: "Invalid payload" }, { status: 400 });
    }

    // Honeypot spam védelem
    if ((parse.data.website_company_field ?? "").trim() !== "") {
      // csendes no-op
      return new NextResponse(null, { status: 204 });
    }

    const email = parse.data.email.trim().toLowerCase();
    
    // MX record ellenőrzés
    if (!(await hasMxRecord(email))) {
      return NextResponse.json(
        { error: "Invalid email domain (no MX records)" },
        { status: 400 }
      );
    }

    const referer = req.headers.get("referer") || "";
    // ha a source tartalmaz "hu"-t VAGY a referer útvonala hu-t tartalmaz → "hu", különben "en"
    const source = parse.data.source ?? "website";
    const locale =
      /(^|\/)(hu)(\/|$)/i.test(referer) || /hu/i.test(source) ? "hu" : "en";

    const listId = Number(process.env.BREVO_LIST_ID ?? 0);
    if (!listId) {
      return NextResponse.json({ error: "BREVO_LIST_ID missing" }, { status: 500 });
    }

    // Idempotens create-or-update kontakt
    const res = await fetch(`${brevoBase}/contacts`, {
      method: "POST",
      headers: brevoHeaders(),
      body: JSON.stringify({
        email,
        listIds: [listId],
        updateEnabled: true,
        attributes: { SOURCE: source, LOCALE: locale },
      }),
      cache: "no-store",
    });

    let details: unknown = null;
    try { details = await res.json(); } catch {}
    
    if (!res.ok) {
      return NextResponse.json({ error: "Brevo error", details }, { status: res.status });
    }

    return NextResponse.json({ ok: true, details });
  } catch (e: unknown) {
    return NextResponse.json({ error: (e as Error)?.message ?? "Server error" }, { status: 500 });
  }
}

// GET/PUT/DELETE metódusok elutasítása
export async function GET() {
  return NextResponse.json({ error: "Method not allowed" }, { status: 405 });
}

export async function PUT() {
  return NextResponse.json({ error: "Method not allowed" }, { status: 405 });
}

export async function DELETE() {
  return NextResponse.json({ error: "Method not allowed" }, { status: 405 });
}