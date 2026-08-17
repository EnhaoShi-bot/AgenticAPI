/* lobehub 模型图标加载器
 *
 * 图标源：@lobehub/icons-static-svg（lobehub 官方静态 SVG 集合，按需异步加载）
 * 命名约定：PascalCase 的图标 key（如 "Qwen"、"OpenAI"）对应包内 kebab-case 文件
 * （qwen.svg / openai.svg），且大多数图标带彩色变体（qwen-color.svg），优先使用彩色。
 *
 * 使用方式见 components/common/LobeIcon.vue；管理员在模型配置里填 lobehub 图标 key 即可。
 */

// 按需异步导入全部 SVG 文本（非 eager：只有真正用到的图标才会进产物）
const modules = import.meta.glob('/node_modules/@lobehub/icons-static-svg/icons/*.svg', {
  query: '?raw',
  import: 'default',
}) as Record<string, () => Promise<string>>

/** 基础名（去掉路径与 .svg 后缀）→ 懒加载器 */
const loaders = new Map<string, () => Promise<string>>()
for (const [path, loader] of Object.entries(modules)) {
  const base = path.slice(path.lastIndexOf('/') + 1, -'.svg'.length)
  loaders.set(base, loader)
}

// 解析结果缓存（null 表示确认无匹配，避免重复查找）
const cache = new Map<string, string | null>()

/** 把 "Qwen" / "OpenAI" / "Gemini.Color" 规范成包内文件基础名 */
function toFileBase(name: string, color: boolean): string {
  // 与 Nexus（new-api 系）约定一致：支持 "Key.Variant" 点号语法，仅取第一段
  const base = (name.split('.')[0] ?? name).trim()
  const kebab = base
    .replace(/([a-z0-9])([A-Z])/g, '$1-$2')
    .replace(/[\s_]+/g, '-')
    .replace(/-+/g, '-')
    .replace(/^-|-$/g, '')
    .toLowerCase()
  return color ? `${kebab}-color` : kebab
}

/** 加载图标 SVG 文本：优先彩色变体，其次单色，都没有返回 null（由调用方兜底） */
export async function loadLobeIconRaw(name: string): Promise<string | null> {
  const key = name.trim()
  if (!key) return null
  if (cache.has(key)) return cache.get(key) ?? null

  for (const base of [toFileBase(key, true), toFileBase(key, false)]) {
    const loader = loaders.get(base)
    if (!loader) continue
    try {
      const svg = await loader()
      // 去掉 <title> 避免 hover 出现浏览器原生提示
      const cleaned = svg.replace(/<title>[\s\S]*?<\/title>/g, '')
      cache.set(key, cleaned)
      return cleaned
    } catch {
      // 加载失败时继续尝试下一个候选
    }
  }
  cache.set(key, null)
  return null
}

/** 调试用：全部可用图标基础名 */
export const allLobeIconNames: string[] = [...loaders.keys()]
