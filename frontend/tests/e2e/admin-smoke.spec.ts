import { expect, test, type Page } from "@playwright/test";

const apiBaseUrl = process.env.PLAYWRIGHT_API_BASE_URL ?? "http://localhost:18000/api/v1";

async function loginAsAdmin(page: Page) {
  await page.goto("/login");
  await page.getByLabel("Email").fill("admin@example.com");
  await page.getByLabel("Mật khẩu").fill("password123");
  await page.getByRole("button", { name: "Đăng nhập" }).click();
  await expect(page).toHaveURL(/\/dashboard$/);
  await expect(page.getByRole("heading", { name: "Xin chào, Chủ đầu tư" })).toBeVisible();
}

async function getPayableInvoiceId(page: Page) {
  const response = await page.request.get(`${apiBaseUrl}/invoices`);
  expect(response.ok()).toBeTruthy();
  const body = (await response.json()) as {
    items: Array<{ id: number; total_amount: number; paid_amount: number }>;
  };
  const invoice = body.items.find((item) => item.paid_amount < item.total_amount);
  expect(invoice).toBeTruthy();
  return invoice!.id;
}

test("redirects protected dashboard visitors to login", async ({ page }) => {
  await page.goto("/dashboard");
  await expect(page).toHaveURL(/\/login$/);
  await expect(page.getByRole("heading", { name: "NhàTrọ Pro" })).toBeVisible();
});

test("logs in and opens the dashboard", async ({ page }) => {
  await loginAsAdmin(page);
  await expect(page.getByText("Tổng thu tháng")).toBeVisible();
  await expect(page.getByText("Dòng tiền")).toBeVisible();
});

test("creates a building with generated rooms and records a payment", async ({ page }) => {
  await loginAsAdmin(page);

  const suffix = Date.now();
  const buildingName = `PW House ${suffix}`;
  await page.goto("/buildings");
  await page.getByRole("link", { name: "Thêm nhà" }).click();
  await page.getByLabel("Mã nhà").fill(`PW-${suffix}`);
  await page.getByLabel("Tên nhà").fill(buildingName);
  await page.getByLabel("Địa chỉ").fill("99 Playwright Street");
  await page.getByLabel("Quản lý phụ trách").selectOption({ label: "Staff User" });
  await page.getByLabel("Số tầng").fill("2");
  await page.getByLabel("Giá thuê mặc định").fill("2500000");
  await page.getByLabel("Tiền cọc mặc định").fill("2500000");
  await page.getByLabel("Số phòng tầng 1").fill("2");
  await page.getByLabel("Số phòng tầng 2").fill("3");
  await page.getByLabel("Wifi").check();
  await page.getByLabel("Camera").check();
  await page.getByLabel("Bãi xe").check();
  await page.getByRole("button", { name: "Lưu thông tin" }).click();
  await expect(page).toHaveURL(/\/buildings\/\d+$/);
  const buildingId = page.url().match(/\/buildings\/(\d+)$/)?.[1];
  expect(buildingId).toBeTruthy();
  await expect(page.getByRole("heading", { name: buildingName })).toBeVisible();
  await expect(page.getByText("101")).toBeVisible();
  await expect(page.getByText("102")).toBeVisible();
  await expect(page.getByText("201")).toBeVisible();
  await expect(page.getByText("203")).toBeVisible();
  await expect(page.getByText("Tổng phòng")).toBeVisible();

  await page.getByRole("link", { name: "101" }).click();
  await expect(page.getByRole("heading", { name: `PW-${suffix}-101` })).toBeVisible();
  await page.getByRole("link", { name: "Sửa" }).click();
  const editedRoomName = `A1-${suffix}`;
  const editedRoomCode = `PW-${suffix}-${editedRoomName}`;
  await page.getByLabel("Tên phòng").fill(editedRoomName);
  await page.getByLabel("Loại phòng").selectOption("studio");
  await page.getByLabel("Số người tối đa").fill("3");
  await page.getByLabel("Trạng thái").selectOption("reserved");
  await page.getByLabel("Ghi chú").fill("Playwright room note");
  await page.getByRole("button", { name: "Lưu thông tin" }).click();
  await expect(page.getByRole("heading", { name: editedRoomCode })).toBeVisible();
  await expect(page.getByText("Đã giữ chỗ")).toBeVisible();
  await expect(page.getByText("Studio")).toBeVisible();

  await page.goto(`/rooms?building_id=${buildingId}&status=reserved&search=${editedRoomName}`);
  await expect(page.getByRole("link", { name: editedRoomCode })).toBeVisible();

  await page.goto("/rooms/create");
  await page.getByLabel("Nhà").selectOption({ label: `PW-${suffix} - ${buildingName}` });
  await page.getByLabel("Tầng").selectOption({ label: "Floor 1" });
  await page.getByLabel("Tên phòng").fill(`109-${suffix}`);
  await page.getByLabel("Giá thuê").fill("2600000");
  await page.getByLabel("Tiền cọc").fill("2600000");
  await page.getByRole("button", { name: "Lưu thông tin" }).click();
  await expect(page.getByRole("heading", { name: `PW-${suffix}-109-${suffix}` })).toBeVisible();

  await page.goto(`/buildings/${buildingId}`);
  await page.getByRole("link", { name: "Sửa" }).click();
  await page.getByLabel("Trạng thái").selectOption("under_renovation");
  await page.getByLabel("Bảo vệ").check();
  await page.getByRole("button", { name: "Lưu thông tin" }).click();
  await expect(page).toHaveURL(/\/buildings\/\d+$/);
  await expect(page.getByText("Đang sửa chữa")).toBeVisible();
  await expect(page.getByText("Bảo vệ")).toBeVisible();

  const invoiceId = await getPayableInvoiceId(page);
  const method = `playwright-${Date.now()}`;
  await page.goto("/payments");
  await page.getByLabel("ID hóa đơn").fill(String(invoiceId));
  await page.getByLabel("Số tiền").fill("1");
  await page.getByLabel("Phương thức").fill(method);
  await page.getByRole("button", { name: "Thêm" }).click();
  await expect(page.getByRole("cell", { name: method })).toBeVisible();
});
