import { BaseDirectory, createDir, readTextFile, writeTextFile } from '@tauri-apps/api/fs';
import { appDataDir, join } from '@tauri-apps/api/path';
import { open } from '@tauri-apps/api/shell';

const APP_DIR = 'post-translator';

const ensureBaseDir = async () => {
  await createDir(APP_DIR, { dir: BaseDirectory.AppData, recursive: true });
};

const resolvePath = async (relativePath: string) => {
  await ensureBaseDir();
  return join(await appDataDir(), APP_DIR, relativePath);
};

export const savePrompt = async (translationKey: string, locale: string, content: string) => {
  const path = `${APP_DIR}/outputs/prompts/${translationKey}-${locale}.txt`;
  await createDir(`${APP_DIR}/outputs/prompts`, { dir: BaseDirectory.AppData, recursive: true });
  await writeTextFile(path, content, { dir: BaseDirectory.AppData });
  return path;
};

export const saveExportJson = async (translationKey: string, content: string) => {
  const path = `${APP_DIR}/exports/${translationKey}-payload.json`;
  await createDir(`${APP_DIR}/exports`, { dir: BaseDirectory.AppData, recursive: true });
  await writeTextFile(path, content, { dir: BaseDirectory.AppData });
  return path;
};

export const exportMdxFiles = async (payload: Record<string, string>) => {
  await createDir(`${APP_DIR}/exports/mdx`, { dir: BaseDirectory.AppData, recursive: true });
  const results: string[] = [];

  for (const [relativePath, content] of Object.entries(payload)) {
    const fullPath = `${APP_DIR}/exports/${relativePath}`;
    const dirName = fullPath.split('/').slice(0, -1).join('/');
    await createDir(dirName, { dir: BaseDirectory.AppData, recursive: true });
    await writeTextFile(fullPath, content, { dir: BaseDirectory.AppData });
    results.push(fullPath);
  }

  return results;
};

export const openExportsFolder = async () => {
  const target = await resolvePath('exports');
  await open(target);
};

export const getAppDataPath = async () => resolvePath('');
