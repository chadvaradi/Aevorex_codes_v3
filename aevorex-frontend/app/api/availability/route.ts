import { NextRequest, NextResponse } from "next/server";
import { AvailabilityService } from "../../../lib/calendar_consulting/availability-service";
import { DateTime } from "luxon";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";
// ISR revalidate fallback
export const revalidate = 60;

function jsonWithCache(body: unknown, init?: ResponseInit) {
  const res = NextResponse.json(body, init);
  res.headers.set("Cache-Control", "s-maxage=60, stale-while-revalidate=120");
  return res;
}

export async function GET(request: NextRequest) {
  try {
    if (!process.env.ICS_FEED_URLS?.trim()) {
      return jsonWithCache(
        { error: "Availability temporarily unavailable" },
        { status: 503 }
      );
    }

    const { searchParams } = new URL(request.url);
    const tz = "Europe/Budapest";

    const now = DateTime.now().setZone(tz);
    const defaultStart = now.startOf("day");
    const defaultEnd = now.plus({ days: 14 }).endOf("day");

    const startParam = searchParams.get("start");
    const endParam = searchParams.get("end");

    let start = startParam ? DateTime.fromISO(startParam).setZone(tz) : defaultStart;
    let end = endParam ? DateTime.fromISO(endParam).setZone(tz) : defaultEnd;

    // Ha parse hiba, vissza defaultokra
    if (!start.isValid) start = defaultStart;
    if (!end.isValid) end = defaultEnd;

    // Clamp: max 30 napos ablak
    const maxEnd = start.plus({ days: 30 });
    if (end > maxEnd) end = maxEnd;

    // Ha fordított sorrend jön, cseréljük
    if (end <= start) end = start.plus({ days: 1 });

    const service = new AvailabilityService();
    const slots = await service.getAvailableSlots({
      startDate: start.toJSDate(),
      endDate: end.toJSDate(),
    });

    return jsonWithCache(slots, { status: 200 });
  } catch (error) {
    console.error("Availability API error:", error);
    return jsonWithCache({ error: "Failed to fetch availability" }, { status: 500 });
  }
}