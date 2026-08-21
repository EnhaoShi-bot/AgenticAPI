/* 由于模型信息需要在多个组件中使用，所以需要使用pinia来管理模型信息 */
import {defineStore} from 'pinia'
import type {modelInfoSchema} from '@/types'
import {getModels} from '@/api/models'
import {ref, computed} from 'vue'


// 统一的模型列表管理，可在多个组件中使用
export const useModelListStore = defineStore('modelList', () => { // 当前pinia的ID，必填项
    // 从API请求得到的模型列表
    const totalModelList = ref<modelInfoSchema[]>([])

    // 计算属性
    const totalModelNumber = computed(() => totalModelList.value.length)
    const freeModelNumber = computed(() => totalModelList.value.filter(model => model.modelGroup === 'free').length)

    // 加载模型列表的方法
    function loadTotalModels() {
        getModels()
            .then(res => {
                // ✅ 在赋值前统一处理 inputPrice，截断为2位小数
                totalModelList.value = res.data.map((model) => ({
                    ...model,
                    inputPrice: Math.floor(model.inputPrice * 100) / 100,
                    outputPrice: Math.floor(model.outputPrice * 100) / 100,
                    cachePrice: Math.floor(model.cachePrice * 100) / 100
                }))
            })
            .catch(error => {
                console.error('加载模型列表失败:', error)
            })
    }

    // 返回3个数据，以及一个方法
    return {
        totalModelList,
        totalModelNumber,
        freeModelNumber,
        loadTotalModels
    }
})
