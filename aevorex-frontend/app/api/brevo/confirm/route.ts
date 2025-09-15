import { NextResponse } from "next/server";
import { consumeToken } from "@/lib/tokens";
import { brevoBase, brevoHeaders } from "@/lib/brevo/client";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET(req: Request) {
  const url = new URL(req.url);
  const token = url.searchParams.get("token") || "";
  const email = consumeToken(token);
  if (!email) {
    return NextResponse.redirect(`${process.env.NEXT_PUBLIC_BASE_URL}/subscribe/invalid`, 302);
  }

  const listId = Number(process.env.BREVO_LIST_ID ?? 0);
  if (!listId) return NextResponse.json({ error: "BREVO_LIST_ID missing" }, { status: 500 });

  // Jelöld confirmed-re (ATTR: STATUS="confirmed") vagy tedd listába ekkor
  await fetch(`${brevoBase}/contacts`, {
    method: "POST",
    headers: brevoHeaders(),
    body: JSON.stringify({
      email,
      listIds: [listId],
      updateEnabled: true,
      attributes: { STATUS: "confirmed" },
    }),
    cache: "no-store",
  }).catch(() => {});

  return NextResponse.redirect(`${process.env.NEXT_PUBLIC_BASE_URL}/subscribe/ok`, 302);
}
