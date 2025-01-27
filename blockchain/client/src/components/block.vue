<template>
  <div>
    <el-card shadow="hover">
  <el-row type="flex" justify="space-between">
    <el-col>
    <el-form
      ref="searchblock"
      :model="searchblock"
      size="small"
      inline="true"
      >
      <el-form-item label="区块号：" prop="index">
        <el-input
          v-model.trim="searchblock.index"
          placeholder="请输入区块号"
          />
      </el-form-item>
      <el-form-item>
        <el-button
          type="primary"
          icon="el-icon-search"
          size="small"
          @click="handleSearch()"
          >查询</el-button>
      </el-form-item>
    </el-form>
      </el-col>
    <el-col>区块高度: {{value}}</el-col>

  </el-row>

  <el-table ref="block":data="BlockData" style="margin-top: 20px" stripe border>
      <el-table-column prop="height" label="区块号" width="100px"/>
      <el-table-column prop="hash" label="区块哈希" show-overflow-tooltip/>
      <el-table-column prop="prevhash" label="上一区块哈希" show-overflow-tooltip/>
      <el-table-column prop="time" label="出块时间" width="200px" show-overflow-tooltip/>
      <el-table-column prop="nodenum" label="认证节点数" width="100px" show-overflow-tooltip/>

  </el-table>
        <el-table ref="block":data="TransData" style="margin-top: 20px"  stripe border>
      <el-table-column prop="sender" label="发送地址" show-overflow-tooltip/>
      <el-table-column prop="receiver" label="接收地址" show-overflow-tooltip/>
      <el-table-column prop="hash" label="交易hash"  show-overflow-tooltip />
      <el-table-column prop="MD5" label="文件MD5" show-overflow-tooltip/>
      <el-table-column prop="time" label="交易时间" show-overflow-tooltip/>
  </el-table>

</el-card>
  </div>

</template>

<script>
export default {
  data(){
    return{
      value:0,
      TransData:[],
      BlockData:[],
      searchblock:{
        index:''
      },
      searchbloc:{
        index:''
      }
    };
  },
  created(){
    this.GetHeight();
  },
  methods: {
    async GetHeight() {
      const result = await this.$axios.get("/api/searchBlock");
      if (result.data.success) {
        this.value = result.data.height;
      } else {
        this.$message.error(result.data.msg);
      }
    },
    async handleSearch() {
      const result = await this.$axios.get("/api/searchBlock", {
        params: {height:this.searchblock.index}
      });
      if (result.data.success) {
        this.BlockData = result.data.BlockData;
        this.TransData=result.data.TransData;
      } else {
        this.BlockData = [];
        this.TransData=[];
        this.$message.error(result.data.message);
      }


    }
  }
}
</script>

<style scoped>

</style>
