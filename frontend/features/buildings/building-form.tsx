"use client";

import { Save } from "lucide-react";
import { useRouter } from "next/navigation";
import type { FormEvent } from "react";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { browserApiPatch, browserApiPost } from "@/lib/api/client";
import type { Building, User } from "@/lib/api/types";

const houseTypes = [
  ["boarding_house", "Nhà trọ"],
  ["mini_apartment", "Chung cư mini"],
  ["dormitory", "Ký túc xá"],
  ["whole_house", "Nhà nguyên căn"],
] as const;

const statuses = [
  ["active", "Đang hoạt động"],
  ["temporarily_closed", "Tạm đóng"],
  ["under_renovation", "Đang sửa chữa"],
] as const;

const amenities = [
  ["wifi", "Wifi"],
  ["camera", "Camera"],
  ["elevator", "Thang máy"],
  ["shared_washing_machine", "Máy giặt chung"],
  ["parking", "Bãi xe"],
  ["security", "Bảo vệ"],
] as const;

type FloorRow = {
  floor_number: number;
  name: string;
  expected_room_count: number;
};

type ExpenseRow = {
  category: string;
  name: string;
  default_amount: number;
  is_active: boolean;
};

export function BuildingForm({
  building,
  mode,
  staffUsers,
}: {
  building?: Building;
  mode: "create" | "edit";
  staffUsers: User[];
}) {
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);
  const [numberOfFloors, setNumberOfFloors] = useState(building?.number_of_floors || 2);
  const [floorRows, setFloorRows] = useState<FloorRow[]>([
    { floor_number: 1, name: "Floor 1", expected_room_count: 2 },
    { floor_number: 2, name: "Floor 2", expected_room_count: 2 },
  ]);
  const [selectedAmenities, setSelectedAmenities] = useState<string[]>(building?.amenities || []);
  const [expenseRows, setExpenseRows] = useState<ExpenseRow[]>(
    building?.expense_templates.length
      ? building.expense_templates.map((template) => ({
          category: template.category,
          name: template.name,
          default_amount: template.default_amount,
          is_active: template.is_active,
        }))
      : [
          { category: "internet", name: "Wifi", default_amount: 300000, is_active: true },
          { category: "security", name: "Security", default_amount: 2000000, is_active: true },
          { category: "cleaning", name: "Cleaning", default_amount: 500000, is_active: true },
        ],
  );

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    const formData = new FormData(event.currentTarget);
    const payload = {
      code: valueOrNull(formData.get("code")),
      name: String(formData.get("name") || ""),
      address: String(formData.get("address") || ""),
      house_type: String(formData.get("house_type") || "boarding_house"),
      number_of_floors: numberOfFloors,
      owner_name: valueOrNull(formData.get("owner_name")),
      owner_phone: valueOrNull(formData.get("owner_phone")),
      owner_email: valueOrNull(formData.get("owner_email")),
      manager_id: numberOrNull(formData.get("manager_id")),
      status: String(formData.get("status") || "active"),
      phone: valueOrNull(formData.get("phone")),
      email: valueOrNull(formData.get("email")),
      zalo: valueOrNull(formData.get("zalo")),
      emergency_contact_name: valueOrNull(formData.get("emergency_contact_name")),
      emergency_contact_phone: valueOrNull(formData.get("emergency_contact_phone")),
      note: valueOrNull(formData.get("note")),
      amenities: selectedAmenities,
      expense_templates: expenseRows.filter((row) => row.category && row.name),
    };
    const createPayload = {
      ...payload,
      default_room_rent_price: numberOrNull(formData.get("default_room_rent_price")),
      default_room_deposit_amount: Number(formData.get("default_room_deposit_amount") || 0),
      default_room_area_sqm: numberOrNull(formData.get("default_room_area_sqm")),
      floors: floorRows,
    };

    try {
      const result =
        mode === "create"
          ? await browserApiPost<Building>("/buildings", createPayload)
          : await browserApiPatch<Building>(`/buildings/${building?.id}`, payload);
      router.push(`/buildings/${result.id}`);
      router.refresh();
    } catch {
      setError("Không lưu được thông tin nhà. Kiểm tra dữ liệu và thử lại.");
    }
  }

  function toggleAmenity(amenityKey: string) {
    setSelectedAmenities((current) =>
      current.includes(amenityKey)
        ? current.filter((item) => item !== amenityKey)
        : [...current, amenityKey],
    );
  }

  return (
    <form className="space-y-6" onSubmit={onSubmit}>
      <Card>
        <h2 className="text-base font-semibold text-ink">Thông tin cơ bản</h2>
        <div className="mt-4 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <Field label="Mã nhà" name="code" defaultValue={building?.code} placeholder="HOUSE-001" />
          <Field label="Tên nhà" name="name" defaultValue={building?.name} required />
          <Field label="Địa chỉ" name="address" defaultValue={building?.address} required />
          <label className="space-y-1">
            <span className="text-xs font-medium text-slate-500">Loại nhà</span>
            <select
              className="h-10 w-full rounded-md border border-border bg-white px-3 text-sm"
              defaultValue={building?.house_type || "boarding_house"}
              name="house_type"
            >
              {houseTypes.map(([value, label]) => (
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
              defaultValue={building?.status || "active"}
              name="status"
            >
              {statuses.map(([value, label]) => (
                <option key={value} value={value}>
                  {label}
                </option>
              ))}
            </select>
          </label>
          <label className="space-y-1">
            <span className="text-xs font-medium text-slate-500">Quản lý phụ trách</span>
            <select
              className="h-10 w-full rounded-md border border-border bg-white px-3 text-sm"
              defaultValue={building?.manager_id ?? ""}
              name="manager_id"
            >
              <option value="">Chưa chọn</option>
              {staffUsers.map((user) => (
                <option key={user.id} value={user.id}>
                  {user.full_name}
                </option>
              ))}
            </select>
          </label>
          {mode === "create" ? (
            <>
              <Field
                label="Số tầng"
                name="number_of_floors_display"
                onChange={changeNumberOfFloors}
                type="number"
                value={numberOfFloors}
              />
              <Field label="Giá thuê mặc định" name="default_room_rent_price" required type="number" />
              <Field label="Tiền cọc mặc định" name="default_room_deposit_amount" type="number" />
              <Field label="Diện tích mặc định" name="default_room_area_sqm" type="number" />
            </>
          ) : null}
        </div>
      </Card>

      <Card>
        <h2 className="text-base font-semibold text-ink">Liên hệ</h2>
        <div className="mt-4 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <Field label="Chủ nhà" name="owner_name" defaultValue={building?.owner_name} />
          <Field label="SĐT chủ nhà" name="owner_phone" defaultValue={building?.owner_phone} />
          <Field label="Email chủ nhà" name="owner_email" defaultValue={building?.owner_email} />
          <Field label="Số điện thoại" name="phone" defaultValue={building?.phone} />
          <Field label="Email" name="email" defaultValue={building?.email} />
          <Field label="Zalo" name="zalo" defaultValue={building?.zalo} />
          <Field
            label="Người liên hệ khẩn cấp"
            name="emergency_contact_name"
            defaultValue={building?.emergency_contact_name}
          />
          <Field
            label="SĐT khẩn cấp"
            name="emergency_contact_phone"
            defaultValue={building?.emergency_contact_phone}
          />
        </div>
      </Card>

      {mode === "create" ? (
        <Card>
          <h2 className="text-base font-semibold text-ink">Cấu trúc tầng</h2>
          <div className="mt-4 grid gap-3">
            {floorRows.map((row, index) => (
              <div className="grid gap-3 md:grid-cols-[120px_1fr_180px]" key={row.floor_number}>
                <Input readOnly value={`Tầng ${row.floor_number}`} />
                <Input
                  aria-label={`Tên tầng ${row.floor_number}`}
                  value={row.name}
                  onChange={(event) =>
                    setFloorRows((current) =>
                      current.map((item, itemIndex) =>
                        itemIndex === index ? { ...item, name: event.target.value } : item,
                      ),
                    )
                  }
                />
                <Input
                  aria-label={`Số phòng tầng ${row.floor_number}`}
                  min={0}
                  type="number"
                  value={row.expected_room_count}
                  onChange={(event) =>
                    setFloorRows((current) =>
                      current.map((item, itemIndex) =>
                        itemIndex === index
                          ? { ...item, expected_room_count: Number(event.target.value || 0) }
                          : item,
                      ),
                    )
                  }
                />
              </div>
            ))}
          </div>
        </Card>
      ) : null}

      <Card>
        <h2 className="text-base font-semibold text-ink">Tiện ích</h2>
        <div className="mt-4 grid gap-3 md:grid-cols-3">
          {amenities.map(([value, label]) => (
            <label className="flex items-center gap-2 text-sm text-slate-700" key={value}>
              <input
                checked={selectedAmenities.includes(value)}
                onChange={() => toggleAmenity(value)}
                type="checkbox"
              />
              {label}
            </label>
          ))}
        </div>
      </Card>

      <Card>
        <h2 className="text-base font-semibold text-ink">Chi phí chung hằng tháng</h2>
        <div className="mt-4 grid gap-3">
          {expenseRows.map((row, index) => (
            <div className="grid gap-3 md:grid-cols-[1fr_1fr_180px]" key={`${row.category}-${index}`}>
              <Input
                aria-label={`Danh mục chi phí ${index + 1}`}
                value={row.category}
                onChange={(event) => updateExpenseRow(index, "category", event.target.value)}
              />
              <Input
                aria-label={`Tên chi phí ${index + 1}`}
                value={row.name}
                onChange={(event) => updateExpenseRow(index, "name", event.target.value)}
              />
              <Input
                aria-label={`Số tiền chi phí ${index + 1}`}
                type="number"
                value={row.default_amount}
                onChange={(event) =>
                  updateExpenseRow(index, "default_amount", Number(event.target.value || 0))
                }
              />
            </div>
          ))}
        </div>
      </Card>

      <Card>
        <label className="space-y-1">
          <span className="text-xs font-medium text-slate-500">Ghi chú</span>
          <textarea
            className="min-h-24 w-full rounded-md border border-border px-3 py-2 text-sm"
            defaultValue={building?.note ?? ""}
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

  function updateExpenseRow<K extends keyof ExpenseRow>(index: number, key: K, value: ExpenseRow[K]) {
    setExpenseRows((current) =>
      current.map((row, rowIndex) => (rowIndex === index ? { ...row, [key]: value } : row)),
    );
  }

  function changeNumberOfFloors(value: string) {
    const nextCount = Number(value || 0);
    setNumberOfFloors(nextCount);
    setFloorRows((current) =>
      Array.from({ length: nextCount }, (_, index) => {
        const floorNumber = index + 1;
        const currentRow = current[index];
        return {
          floor_number: floorNumber,
          name: currentRow?.name || `Floor ${floorNumber}`,
          expected_room_count: currentRow?.expected_room_count ?? 1,
        };
      }),
    );
  }
}

function Field({
  defaultValue,
  label,
  name,
  onChange,
  placeholder,
  required,
  type = "text",
  value,
}: {
  defaultValue?: string | number | null;
  label: string;
  name: string;
  onChange?: (value: string) => void;
  placeholder?: string;
  required?: boolean;
  type?: "text" | "number";
  value?: string | number;
}) {
  return (
    <label className="space-y-1">
      <span className="text-xs font-medium text-slate-500">{label}</span>
      <Input
        defaultValue={value === undefined ? (defaultValue ?? "") : undefined}
        min={type === "number" ? 0 : undefined}
        name={name}
        onChange={onChange ? (event) => onChange(event.target.value) : undefined}
        placeholder={placeholder}
        required={required}
        type={type}
        value={value}
      />
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
