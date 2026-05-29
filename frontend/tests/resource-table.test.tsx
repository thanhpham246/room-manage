import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { ResourceTable } from "@/features/resources/resource-table";

describe("ResourceTable", () => {
  it("renders an empty state", () => {
    render(<ResourceTable columns={[{ key: "name", label: "Tên" }]} items={[]} />);

    expect(screen.getByText("Chưa có dữ liệu")).toBeInTheDocument();
  });

  it("renders rows", () => {
    render(
      <ResourceTable
        columns={[{ key: "name", label: "Tên" }]}
        items={[{ id: 1, name: "Phòng 101" }]}
      />,
    );

    expect(screen.getByText("Phòng 101")).toBeInTheDocument();
  });
});
