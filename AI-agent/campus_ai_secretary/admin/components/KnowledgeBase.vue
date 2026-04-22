<template>
    <div>
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
            <div>
                <el-input 
                    v-model="searchQuery" 
                    placeholder="搜索知识库内容" 
                    style="width: 300px;"
                    @input="searchKnowledge"
                ></el-input>
            </div>
            <el-button type="primary" @click="showAddKnowledge = true">添加知识</el-button>
        </div>

        <el-table 
            :data="knowledgeStore.knowledgeList" 
            border 
            style="width: 100%;"
            :loading="knowledgeStore.loading"
        >
            <el-table-column prop="id" label="ID" width="80"></el-table-column>
            <el-table-column prop="title" label="标题"></el-table-column>
            <el-table-column prop="category" label="分类">
                <template #default="scope">
                    <el-tag type="info">{{ scope.row.category }}</el-tag>
                </template>
            </el-table-column>
            <el-table-column prop="source_type" label="来源" width="100"></el-table-column>
            <el-table-column prop="created_at" label="创建时间" width="180"></el-table-column>
            <el-table-column label="操作" width="150">
                <template #default="scope">
                    <el-button size="small" @click="viewKnowledge(scope.row)">查看</el-button>
                    <el-button size="small" type="danger" @click="deleteKnowledge(scope.row.id)">删除</el-button>
                </template>
            </el-table-column>
        </el-table>

        <el-dialog title="添加知识" v-model="showAddKnowledge">
            <el-form :model="knowledgeForm" :rules="knowledgeRules" ref="knowledgeFormRef">
                <el-form-item prop="title">
                    <el-input v-model="knowledgeForm.title" placeholder="标题"></el-input>
                </el-form-item>
                <el-form-item prop="content">
                    <el-textarea v-model="knowledgeForm.content" placeholder="内容" :rows="5"></el-textarea>
                </el-form-item>
                <el-form-item prop="category">
                    <el-select v-model="knowledgeForm.category" placeholder="分类">
                        <el-option label="学习资料" value="学习资料"></el-option>
                        <el-option label="通知公告" value="通知公告"></el-option>
                        <el-option label="常见问题" value="常见问题"></el-option>
                        <el-option label="AI分析" value="AI分析"></el-option>
                        <el-option label="其他" value="其他"></el-option>
                    </el-select>
                </el-form-item>
            </el-form>
            <template #footer>
                <el-button @click="showAddKnowledge = false">取消</el-button>
                <el-button type="primary" @click="submitKnowledge">确定</el-button>
            </template>
        </el-dialog>

        <el-dialog title="知识详情" v-model="showViewKnowledge">
            <h4>{{ viewItem.title }}</h4>
            <div style="margin-top: 15px; padding: 10px; background: #f5f5f5; border-radius: 4px;">
                {{ viewItem.content }}
            </div>
        </el-dialog>
    </div>
</template>

<script>
export default {
    name: 'KnowledgeBase',
    data() {
        return {
            searchQuery: '',
            showAddKnowledge: false,
            showViewKnowledge: false,
            viewItem: {},
            knowledgeForm: {
                title: '',
                content: '',
                category: '学习资料'
            },
            knowledgeRules: {
                title: [{ required: true, message: '请输入标题', trigger: 'blur' }],
                content: [{ required: true, message: '请输入内容', trigger: 'blur' }]
            }
        };
    },
    mounted() {
        this.loadKnowledge();
    },
    methods: {
        async loadKnowledge() {
            await knowledgeStore.loadKnowledge();
        },
        searchKnowledge() {
            knowledgeStore.searchKnowledge(this.searchQuery);
        },
        viewKnowledge(item) {
            this.viewItem = item;
            this.showViewKnowledge = true;
        },
        async deleteKnowledge(id) {
            if (await this.$confirm('确定要删除该知识吗？')) {
                await knowledgeStore.deleteKnowledge(id);
                this.$message.success('删除成功');
            }
        },
        async submitKnowledge() {
            await knowledgeStore.createKnowledge(this.knowledgeForm);
            this.showAddKnowledge = false;
            this.knowledgeForm = { title: '', content: '', category: '学习资料' };
            this.$message.success('添加成功');
            await this.loadKnowledge();
        }
    }
};
</script>
