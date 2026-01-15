/**
 * 文章接口
 * @author <a href="https://codefather.cn">编程导航学习圈</a>
 */
import request from '@/request'

/**
 * 创建文章请求
 */
export interface ArticleCreateRequest {
  topic: string
}

/**
 * 文章查询请求
 */
export interface ArticleQueryRequest {
  pageNum?: number
  pageSize?: number
  userId?: number
  status?: string
}

/**
 * 文章VO
 */
export interface ArticleVO {
  id: number
  taskId: string
  userId: number
  topic: string
  mainTitle: string
  subTitle: string
  outline: OutlineItem[]
  content: string
  images: ImageItem[]
  status: string
  errorMessage?: string
  createTime: string
  completedTime?: string
}

export interface OutlineItem {
  section: number
  title: string
  points: string[]
}

export interface ImageItem {
  position: number
  url: string
  method: string
  keywords: string
  description: string
}

/**
 * 创建文章任务
 */
export const createArticle = (data: ArticleCreateRequest) => {
  return request.post<string>('/article/create', data)
}

/**
 * 获取文章详情
 */
export const getArticle = (taskId: string) => {
  return request.get<ArticleVO>(`/article/${taskId}`)
}

/**
 * 分页查询文章列表
 */
export const listArticle = (data: ArticleQueryRequest) => {
  return request.post<any>('/article/list', data)
}

/**
 * 删除文章
 */
export const deleteArticle = (id: number) => {
  return request.post<boolean>('/article/delete', { id })
}
