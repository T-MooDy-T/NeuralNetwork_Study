<template>
    <div>
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
            <div>
                <el-input 
                    v-model="searchQuery" 
                    placeholder="搜索采集信息" 
                    style="width: 300px;"
                    @input="searchCollected"
                ></el-input>
            </div>
            <el-button type="primary" @click="collectInfo">采集信息</el-button>
        </div>

        <el-table 
            :data="collectedStore.collectedList" 
            border 
            style="width: 100%;"
            :loading="collectedStore.loading"
        >
            <el-table-column prop="id" label="ID" width="80"></el-table-column>
            <el-table-column prop="source" label="来源"></el-table-column>
            <el-table-column prop="content" label="内容"></el-table-column>
            <el-table-column prop="source_type" label="类型" width="100">
                <template #default="scope">
                    <el-tag type="info">{{ scope.row.source_type }}</el-tag>
                </template>
            </el-table-column>
            <el-table-column prop="created_at" label="采集时间" width="180"></el-table-column>
            <el-table-column label="操作" width="150">
                <template #default="scope">
                    <el-button size="small" type="danger" @click="deleteCollected(scope.row.id)">删除</el-button>
                </template>
            </el-table-column>
        </el-table>
    </div>
</template>

<script>
export default {
    name: 'CollectedInfo',
    data() {
        return {
            searchQuery: ''
        };
    },
    mounted() {
        this.loadCollected();
    },
    methods: {
        async loadCollected() {
            await collectedStore.loadCollected();
        },
        searchCollected() {
            collectedStore.searchCollected(this.searchQuery);
        },
        async collectInfo() {
            await collectedStore.collectInfo();
            this.$message.success('采集成功');
            await this.loadCollected();
        },
        async deleteCollected(id) {
            if (await this.$confirm('确定要删除该采集信息吗？')) {
                await collectedStore.deleteCollected(id);
                this.$message.success('删除成功');
            }
        }
    }
};
</script>
