import { ArrowLeft, Pencil } from "lucide-react";
import Link from "next/link";
import { notFound } from "next/navigation";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { amenityLabel, buildingStatusLabel, houseTypeLabel } from "@/features/buildings/labels";
import { getBuilding, getBuildingDashboard, getBuildingTree } from "@/lib/api/server";
import { formatVnd } from "@/lib/formatters/currency";

export default async function BuildingDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const buildingId = Number(id);
  const [building, dashboard, tree] = await Promise.all([
    getBuilding(buildingId),
    getBuildingDashboard(buildingId),
    getBuildingTree(buildingId),
  ]);
  if (!building || !dashboard || !tree) {
    notFound();
  }

  const kpis = [
    { label: "Tổng phòng", value: String(dashboard.total_rooms) },
    { label: "Đang thuê", value: String(dashboard.occupied_rooms) },
    { label: "Phòng trống", value: String(dashboard.vacant_rooms) },
    { label: "Tỷ lệ lấp đầy", value: `${dashboard.occupancy_rate}%` },
    { label: "Doanh thu tháng", value: formatVnd(dashboard.monthly_revenue) },
    { label: "Công nợ", value: formatVnd(dashboard.debt) },
    { label: "Sắp hết hạn", value: `${dashboard.expiring_contracts} HĐ` },
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <Link
            className="mb-3 inline-flex items-center gap-2 text-sm text-slate-500 hover:text-ink"
            href="/buildings"
          >
            <ArrowLeft className="size-4" />
            Quay lại danh sách
          </Link>
          <div className="flex flex-wrap items-center gap-3">
            <h1 className="text-2xl font-semibold text-ink">{building.name}</h1>
            <Badge tone="green">{buildingStatusLabel(building.status)}</Badge>
          </div>
          <p className="mt-1 text-sm text-slate-500">
            {building.code} · {houseTypeLabel(building.house_type)} · {building.address}
          </p>
        </div>
        <Link href={`/buildings/${building.id}/edit`}>
          <Button type="button" variant="secondary">
            <Pencil className="size-4" />
            Sửa
          </Button>
        </Link>
      </div>

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {kpis.map((kpi) => (
          <Card className="min-h-28" key={kpi.label}>
            <p className="text-sm text-slate-500">{kpi.label}</p>
            <p className="mt-6 text-2xl font-semibold text-ink">{kpi.value}</p>
          </Card>
        ))}
      </section>

      <section className="grid gap-6 xl:grid-cols-[minmax(0,1fr)_360px]">
        <Card>
          <h2 className="text-lg font-semibold text-ink">Sơ đồ tầng/phòng</h2>
          <div className="mt-4 space-y-4">
            {tree.floors.map((floor) => (
              <div className="rounded-md border border-border p-4" key={floor.id}>
                <div className="flex items-center justify-between gap-3">
                  <h3 className="font-semibold text-ink">{floor.name}</h3>
                  <span className="text-sm text-slate-500">
                    {floor.rooms.length}/{floor.expected_room_count} phòng
                  </span>
                </div>
                <div className="mt-3 flex flex-wrap gap-2">
                  {floor.rooms.map((room) => (
                    <Link href={`/rooms/${room.id}`} key={room.id}>
                      <Badge tone={room.status === "occupied" ? "green" : "slate"}>{room.name}</Badge>
                    </Link>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </Card>

        <div className="space-y-6">
          <Card>
            <h2 className="text-lg font-semibold text-ink">Tiện ích</h2>
            <div className="mt-4 flex flex-wrap gap-2">
              {building.amenities.length === 0 ? (
                <p className="text-sm text-slate-500">Chưa khai báo tiện ích</p>
              ) : (
                building.amenities.map((amenity) => (
                  <Badge key={amenity} tone="slate">
                    {amenityLabel(amenity)}
                  </Badge>
                ))
              )}
            </div>
          </Card>
          <Card>
            <h2 className="text-lg font-semibold text-ink">Chi phí chung</h2>
            <div className="mt-4 space-y-3">
              {building.expense_templates.map((template) => (
                <div className="flex items-center justify-between gap-4 text-sm" key={template.id}>
                  <span className="text-slate-600">{template.name}</span>
                  <span className="font-medium text-ink">{formatVnd(template.default_amount)}</span>
                </div>
              ))}
            </div>
          </Card>
        </div>
      </section>
    </div>
  );
}
