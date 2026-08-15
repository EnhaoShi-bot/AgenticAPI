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
                totalModelList.value = res.data
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
