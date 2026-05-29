"use client";

import { Save } from "lucide-react";
import { useRouter } from "next/navigation";
import type { FormEvent } from "react";
import { useMemo, useState } from "react";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { browserApiPatch, browserApiPost } from "@/lib/api/client";
import type { Room } from "@/lib/api/types";
import { roomStatuses, roomTypes } from "@/features/rooms/labels";

export type RoomFloorOption = {
  building_id: number;
  building_code: string;
  building_name: string;
  floor_id: number;
  floor_name: string;
  floor_number: number;
};

export function RoomForm({
  floorOptions = [],
  mode,
  room,
}: {
  floorOptions?: RoomFloorOption[];
  mode: "create" | "edit";
  room?: Room;
}) {
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);
  const defaultBuildingId = room?.building_id ?? floorOptions[0]?.building_id ?? 0;
  const [selectedBuildingId, setSelectedBuildingId] = useState(defaultBuildingId);
  const buildingOptions = useMemo(
    () =>
      Array.from(
        new Map(
          floorOptions.map((option) => [
            option.building_id,
            {
              id: option.building_id,
              code: option.building_code,
              name: option.building_name,
            },
          ]),
        ).values(),
      ),
    [floorOptions],
  );
  const selectedFloorOptions = floorOptions.filter(
    (option) => option.building_id === selectedBuildingId,
  );

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    const formData = new FormData(event.currentTarget);
    const payload = {
      name: String(formData.get("name") || ""),
      room_type: String(formData.get("room_type") || "standard"),
      area_sqm: numberOrNull(formData.get("area_sqm")),
      max_occupants: Number(formData.get("max_occupants") || 1),
      rent_price: Number(formData.get("rent_price") || 0),
      deposit_amount: Number(formData.get("deposit_amount") || 0),
      status: String(formData.get("status") || "vacant"),
      note: valueOrNull(formData.get("note")),
    };
    const createPayload = {
      ...payload,
      building_id: Number(formData.get("building_id") || 0),
      floor_id: Number(formData.get("floor_id") || 0),
    };

    try {
      const result =
        mode === "create"
          ? await browserApiPost<Room>("/rooms", createPayload)
          : await browserApiPatch<Room>(`/rooms/${room?.id}`, payload);
      router.push(`/rooms/${result.id}`);
      router.refresh();
    } catch {
      setError("Không lưu được thông tin phòng. Kiểm tra dữ liệu và thử lại.");
    }
  }

  return (
    <form className="space-y-6" onSubmit={onSubmit}>
      <Card>
        <h2 className="text-base font-semibold text-ink">Thông tin phòng</h2>
        <div className="mt-4 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          {mode === "create" ? (
            <>
              <label className="space-y-1">
                <span className="text-xs font-medium text-slate-500">Nhà</span>
                <select
                  className="h-10 w-full rounded-md border border-border bg-white px-3 text-sm"
                  name="building_id"
                  onChange={(event) => setSelectedBuildingId(Number(event.target.value))}
                  required
                  value={selectedBuildingId || ""}
                >
                  {buildingOptions.map((building) => (
                    <option key={building.id} value={building.id}>
                      {building.code} - {building.name}
                    </option>
                  ))}
                </select>
              </label>
              <label className="space-y-1">
                <span className="text-xs font-medium text-slate-500">Tầng</span>
                <select
                  className="h-10 w-full rounded-md border border-border bg-white px-3 text-sm"
                  name="floor_id"
                  required
                >
                  {selectedFloorOptions.map((floor) => (
                    <option key={floor.floor_id} value={floor.floor_id}>
                      {floor.floor_name}
                    </option>
                  ))}
                </select>
              </label>
            </>
          ) : (
            <>
              <ReadOnlyField label="Nhà" value={room?.building_name ?? `#${room?.building_id}`} />
              <ReadOnlyField label="Tầng" value={room?.floor_name ?? String(room?.floor ?? "")} />
              <ReadOnlyField label="Mã phòng" value={room?.code ?? ""} />
            </>
          )}
          <Field label="Tên phòng" name="name" defaultValue={room?.name} required />
          <label className="space-y-1">
            <span className="text-xs font-medium text-slate-500">Loại phòng</span>
            <select
              className="h-10 w-full rounded-md border border-border bg-white px-3 text-sm"
              defaultValue={room?.room_type ?? "standard"}
              name="room_type"
            >
              {roomTypes.map(([value, label]) => (
                <option key={value} value={value}>
                  {label}
                </option>
              ))}
            </select>
          </label>
          <label className="space-y-1">
            <span className="text-xs font-medium text-slate-500">Trạng thái</span>
            <select
              className="h-10 w-full rounded-md border border-border bg-white px-3 text-sm"
              defaultValue={room?.status ?? "vacant"}
              name="status"
            >
              {roomStatuses.map(([value, label]) => (
                <option key={value} value={value}>
                  {label}
                </option>
              ))}
            </select>
          </label>
          <Field
            defaultValue={room?.max_occupants ?? 1}
            label="Số người tối đa"
            name="max_occupants"
            required
            type="number"
          />
          <Field label="Diện tích" name="area_sqm" defaultValue={room?.area_sqm} type="number" />
          <Field label="Giá thuê" name="rent_price" defaultValue={room?.rent_price} required type="number" />
          <Field
            label="Tiền cọc"
            name="deposit_amount"
            defaultValue={room?.deposit_amount}
            type="number"
          />
        </div>
      </Card>
      <Card>
        <label className="space-y-1">
          <span className="text-xs font-medium text-slate-500">Ghi chú</span>
          <textarea
            className="min-h-24 w-full rounded-md border border-border px-3 py-2 text-sm"
            defaultValue={room?.note ?? ""}
            name="note"
          />
        </label>
      </Card>
      {error ? <p className="text-sm text-rose-600">{error}</p> : null}
      <Button type="submit">
        <Save className="size-4" />
        Lưu thông tin
      </Button>
    </form>
  );
}

function Field({
  defaultValue,
  label,
  name,
  required,
  type = "text",
}: {
  defaultValue?: string | number | null;
  label: string;
  name: string;
  required?: boolean;
  type?: "text" | "number";
}) {
  return (
    <label className="space-y-1">
      <span className="text-xs font-medium text-slate-500">{label}</span>
      <Input
        defaultValue={defaultValue ?? ""}
        min={type === "number" ? 0 : undefined}
        name={name}
        required={required}
        type={type}
      />
    </label>
  );
}

function ReadOnlyField({ label, value }: { label: string; value: string }) {
  return (
    <label className="space-y-1">
      <span className="text-xs font-medium text-slate-500">{label}</span>
      <Input readOnly value={value} />
    </label>
  );
}

function valueOrNull(value: FormDataEntryValue | null) {
  const text = String(value || "").trim();
  return text.length > 0 ? text : null;
}

function numberOrNull(value: FormDataEntryValue | null) {
  const text = String(value || "").trim();
  return text.length > 0 ? Number(text) : null;
}
