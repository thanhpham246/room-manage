import { describe, expect, it } from "vitest";

import { formatVnd } from "@/lib/formatters/currency";

describe("formatVnd", () => {
  it("formats VND without decimal digits", () => {
    expect(formatVnd(48900000)).toContain("48.900.000");
  });
});
