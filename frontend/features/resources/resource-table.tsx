import { Badge } from "@/components/ui/badge";
import type { ReactNode } from "react";

type Column<T> = {
  key: keyof T | string;
  label: string;
  render?: (item: T) => ReactNode;
};

export function ResourceTable<T extends { id: number }>({
  columns,
  items,
}: {
  columns: Column<T>[];
  items: T[];
}) {
  return (
    <div className="overflow-hidden rounded-lg border border-border bg-white">
      <table className="w-full border-collapse text-left text-sm">
        <thead className="bg-muted text-xs uppercase text-slate-500">
          <tr>
            {columns.map((column) => (
              <th className="px-4 py-3 font-semibold" key={String(column.key)}>
                {column.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {items.length === 0 ? (
            <tr>
              <td className="px-4 py-8 text-center text-slate-500" colSpan={columns.length}>
                Chưa có dữ liệu
              </td>
            </tr>
          ) : (
            items.map((item) => (
              <tr className="border-t border-border" key={item.id}>
                {columns.map((column) => (
                  <td className="px-4 py-3" key={String(column.key)}>
                    {column.render ? column.render(item) : String(item[column.key as keyof T] ?? "")}
                  </td>
                ))}
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}

export function StatusBadge({ status }: { status: string }) {
  const tone = status === "paid" || status === "occupied" || status === "active" ? "green" : "amber";
  return <Badge tone={tone}>{status}</Badge>;
}
