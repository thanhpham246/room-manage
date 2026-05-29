import { ArrowLeft, Pencil } from "lucide-react";
import Link from "next/link";
import { notFound } from "next/navigation";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { roomStatusLabel, roomStatusTone, roomTypeLabel } from "@/features/rooms/labels";
import { getRoomDashboard } from "@/lib/api/server";
import { formatVnd } from "@/lib/formatters/currency";

export default async function RoomDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const dashboard = await getRoomDashboard(Number(id));
  if (!dashboard) {
    notFound();
  }
  const room = dashboard.room;
  const kpis = [
    { label: "Giá thuê", value: formatVnd(room.rent_price) },
    { label: "Tiền cọc", value: formatVnd(room.deposit_amount) },
    { label: "Công nợ", value: formatVnd(dashboard.current_debt) },
    {
      label: "Thanh toán gần nhất",
      value: dashboard.last_payment_amount ? formatVnd(dashboard.last_payment_amount) : "Chưa có",
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <Link
            className="mb-3 inline-flex items-center gap-2 text-sm text-slate-500 hover:text-ink"
            href="/rooms"
          >
            <ArrowLeft className="size-4" />
            Quay lại danh sách
          </Link>
          <div className="flex flex-wrap items-center gap-3">
            <h1 className="text-2xl font-semibold text-ink">{room.code}</h1>
            <Badge tone={roomStatusTone(room.status)}>{roomStatusLabel(room.status)}</Badge>
          </div>
          <p className="mt-1 text-sm text-slate-500">
            {room.building_name} · {room.floor_name ?? `Tầng ${room.floor}`} · {room.name}
          </p>
        </div>
        <Link href={`/rooms/${room.id}/edit`}>
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

      <section className="grid gap-6 xl:grid-cols-2">
        <Card>
          <h2 className="text-lg font-semibold text-ink">Thông tin vận hành</h2>
          <dl className="mt-4 grid gap-3 text-sm">
            <Info label="Loại phòng" value={roomTypeLabel(room.room_type)} />
            <Info label="Số người tối đa" value={`${room.max_occupants} người`} />
            <Info label="Diện tích" value={room.area_sqm ? `${room.area_sqm} m2` : "Chưa nhập"} />
            <Info label="Hợp đồng hiện tại" value={room.active_contract_id ? `#${room.active_contract_id}` : "Không có"} />
          </dl>
        </Card>
        <Card>
          <h2 className="text-lg font-semibold text-ink">Người thuê và hợp đồng</h2>
          <dl className="mt-4 grid gap-3 text-sm">
            <Info label="Người thuê" value={dashboard.tenant_name ?? "Chưa có"} />
            <Info label="Ngày bắt đầu" value={dashboard.contract_start_date ?? "Chưa có"} />
            <Info label="Ngày kết thúc" value={dashboard.contract_end_date ?? "Chưa có"} />
            <Info label="Thanh toán cuối" value={dashboard.last_payment_date ?? "Chưa có"} />
          </dl>
        </Card>
        <Card>
          <h2 className="text-lg font-semibold text-ink">Chỉ số gần nhất</h2>
          <dl className="mt-4 grid gap-3 text-sm">
            <Info label="Tháng" value={dashboard.latest_billing_month ?? "Chưa có"} />
            <Info
              label="Điện"
              value={
                dashboard.latest_electricity_current === null ||
                dashboard.latest_electricity_current === undefined
                  ? "Chưa có"
                  : String(dashboard.latest_electricity_current)
              }
            />
            <Info
              label="Nước"
              value={
                dashboard.latest_water_current === null ||
                dashboard.latest_water_current === undefined
                  ? "Chưa có"
                  : String(dashboard.latest_water_current)
              }
            />
          </dl>
        </Card>
        <Card>
          <h2 className="text-lg font-semibold text-ink">Ghi chú</h2>
          <p className="mt-4 whitespace-pre-wrap text-sm text-slate-600">
            {room.note || "Chưa có ghi chú"}
          </p>
        </Card>
      </section>
    </div>
  );
}

function Info({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between gap-4">
      <dt className="text-slate-500">{label}</dt>
      <dd className="text-right font-medium text-ink">{value}</dd>
    </div>
  );
}
