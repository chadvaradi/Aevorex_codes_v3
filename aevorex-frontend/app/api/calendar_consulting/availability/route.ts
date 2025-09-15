import { NextRequest, NextResponse } from "next/server";
import { AvailabilityService } from "@/lib/calendar_consulting/availability-service";
import { DateTime } from "luxon";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";
// ISR revalidate fallback
export const revalidate = 60;

function jsonWithCache(body: unknown, init?: ResponseInit) {
  return NextResponse.json(body, init);
}

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const start = searchParams.get("start");
    const end = searchParams.get("end");

    if (!start || !end) {
      return jsonWithCache(
        { error: "Missing start or end parameter" },
        { status: 400 }
      );
    }

    const startDate = DateTime.fromISO(start);
    const endDate = DateTime.fromISO(end);

    if (!startDate.isValid || !endDate.isValid) {
      return jsonWithCache(
        { error: "Invalid date format" },
        { status: 400 }
      );
    }

    const service = new AvailabilityService();
    const response = await service.getAvailableSlots({
      startDate: startDate.toJSDate(),
      endDate: endDate.toJSDate()
    });

    return jsonWithCache({
      slots: response.slots,
      slotDurationMin: response.slotDurationMin,
    });
  } catch (error) {
    console.error("Availability API error:", error);
    return jsonWithCache(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
}