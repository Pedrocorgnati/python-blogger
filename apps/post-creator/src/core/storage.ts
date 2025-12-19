import { BaseDirectory, createDir, writeTextFile } from '@tauri-apps/api/fs';
import { appDataDir, join } from '@tauri-apps/api/path';
import { open } from '@tauri-apps/api/shell';

const APP_DIR = 'post-creator';

const ensureBaseDir = async () => {
  await createDir(APP_DIR, { dir: BaseDirectory.AppData, recursive: true });
};

const resolvePath = async (relativePath: string) => {
  await ensureBaseDir();
  return join(await appDataDir(), APP_DIR, relativePath);
};

export const saveEnglishPackage = async (translationKey: string, content: string) => {
  const path = `${APP_DIR}/outputs/shared/en-packages/${translationKey}.json`;
  await createDir(`${APP_DIR}/outputs/shared/en-packages`, {
    dir: BaseDirectory.AppData,
    recursive: true
  });
  await writeTextFile(path, content, { dir: BaseDirectory.AppData });
  return path;
};

export const openExportsFolder = async () => {
  const target = await resolvePath('outputs/shared/en-packages');
  await open(target);
};

export const getAppDataPath = async () => resolvePath('');
