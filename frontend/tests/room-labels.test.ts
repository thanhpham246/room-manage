import { describe, expect, it } from "vitest";

import { roomStatusLabel, roomStatusTone, roomTypeLabel } from "@/features/rooms/labels";

describe("room labels", () => {
  it("renders Vietnamese labels for room metadata", () => {
    expect(roomTypeLabel("studio")).toBe("Studio");
    expect(roomStatusLabel("maintenance")).toBe("Bảo trì");
    expect(roomStatusTone("occupied")).toBe("green");
  });
});
